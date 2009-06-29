"""This is a second generation crawler, compared to
the one contained in crawler.py.  This one is meant
to take advantage of the multiprocessing module in
python, as well as the idea that after fetching the
HTML, a crawler also needs to process the HTML, or
at least output the type of processing that is expected
for a given page.
"""

from multiprocessing import Process, Queue, Pool, pool
from urllib2 import HTTPError
import urlparse

from cobra.steve.util.prelude import *
from cobra.steve.crawler import fetcher, caches
from cobra.steve.third_party.BeautifulSoup import BeautifulSoup
from cobra.steve.indexing import protokv


class SpecialProcess(Process):
  def __init__(self, *args, **kwargs):
    kwargs['target'] = SpecialWorkerFunction
    super(SpecialProcess, self).__init__(*args, **kwargs)


class SpecialPool(pool.Pool):
  Process = SpecialProcess


def SpecialWorkerFunction(inqueue, outqueue, initializer, initargs=()):
  # This is almost a direct copy of the 'worker' function in
  # multiprocessing/pool.py - just with a few specializations that
  # make the type of crawling we're doing easier (as the Pool abstraction
  # doesn't _quite_ let us do what we want)
  put = outqueue.put
  get = inqueue.get
  if hasattr(inqueue, '_writer'):
    inqueue._writer.close()
    outqueue._reader.close()

  url_queue, output_queue = initargs
  # Helper functions that we pass into our task
  def EmitUrl(base_url, url, callback, *args):
    url_queue.put((urlparse.urljoin(base_url, url), callback, args))
  def Output(key, value):
    output_queue.put((key, value.SerializeToString()))

  # The main task loop.
  while True:
    try:
      task = get()
    except (EOFError, IOError):
      break
    if task is None:
      break
    job, i, func, args, kwargs = task
    url = None
    try:
      url, html, args = args
      soup = BeautifulSoup(html)
      result = (True, func(url, soup, partial(EmitUrl, url), Output, *args))
    except TypeError, e:
      
      PrintStackTrace(url, e)
      result = (False, e)
    except Exception, e:
      PrintStackTrace(url, e)
      result = (False, e)
    put((job, i, result))


def RunGrawler(seed_urls, seed_callback, repos, protokv_file_path, protokv_type):
  output_queue = Queue()
  reducer_args = (protokv_file_path, protokv_type, output_queue)
  reducer = Process(target=OutputProcess, args=reducer_args)
  reducer.start()
  url_queue = Queue()
  processor_pool = SpecialPool(initargs=(url_queue, output_queue))
  for url in seed_urls:
    url_queue.put((url, seed_callback, ()))
  FetchingProcess(url_queue, output_queue, processor_pool, repos)


def FetchingProcess(url_queue, output_queue, processor_pool, repos):
  urls_seen = set()
  while True:
    url = None
    try:
      url, callback, args = url_queue.get()
      if url in urls_seen:
        continue
      print "Fetching", url
      urls_seen.add(url)
      html = fetcher.FetchUrl(url, cache_strategy=repos)
      processor_pool.apply_async(callback, (url, html, args))
    except HTTPError, e:
      print "Error fetching %s: %s" % (url, e)
    except Exception, e:
      PrintStackTrace(url, e)


def ProcessCallbackWrapper(callback, url, html, args=()):
  try:
    soup = BeautifulSoup(html)
    urls = []
    if callback is not None:
      callback(url, soup, EmitUrl, Output, *args)
    else:
      print "Callback none!"
  except Exception, e:
    PrintStackTrace(url, e)
    return [], []
  else:
    return urls, outputs


def OutputProcess(protokv_file_path, ProtoKVType, output_queue):
  # This is the most simple implementation of HashFold
  # ever imagined.  Its also horribly specialized here
  # (although, to be fair, MergeFrom is fairly polymorphic).
  #
  # TODO(fedele): transfer as much information as possible out of memory
  # TODO(fedele): figuring out a smarter way to shard/split keys
  # TODO(fedele): implement a real hashing function
  # TODO(fedele): get this to work for other Folding functions?  The lack of destructive update hurts the
  #               setdefault elegance...however, that DOES make a new proto every call.
  # TODO(fedele): move this to its own library someplace
  hashfold = {}
  def Hash(key):
    return str(key)
  try:
    while True:
      key, serialized_value = output_queue.get()
      print "OUTPUT", key
      if key is None:
        break
      value = ProtoKVType()
      value.ParseFromString(serialized_value)
      hashfold.setdefault(Hash(key), ProtoKVType()).MergeFrom(value)
  except KeyboardInterrupt:
    pass
  print "OutputProcess is cleaning up"
  protokv_file = protokv.ProtoKeyValueFile(ProtoKVType, protokv_file_path, 'w')
  for key, value in hashfold.iteritems():
    protokv_file.Output(key, value)
  protokv_file.Close()


def PrintStackTrace(url, err):
  import traceback
  print '-' * 60
  print "Exception while processing %s" % url
  traceback.print_exc(file=sys.stdout)
  print '-' * 60


def ProcessHtmlForEbay(url, soup, EmitUrl):
  print "EBAYYYYY"


def ProcessHtml(url, soup, EmitUrl):
  print "HI", url
  EmitUrl("http://www.ebay.com")
  if url == "http://www.google.com":
    EmitUrl("http://www.amazon.com")
    EmitUrl("http://www.ebay.com")


def main(argv):
  class DummyOutput:
    def Output(key, value):
      pass
  repo = caches.OnDiskCacheStrategy('/tmp/grawlercache')
  seed_urls = ["http://www.google.com"]
  RunGrawler(seed_urls, ProcessHtml, repo, None)


if __name__ == '__main__':
  app.run()
