"""This is a second generation crawler, compared to
the one contained in crawler.py.  This one is meant
to take advantage of the multiprocessing module in
python, as well as the idea that after fetching the
HTML, a crawler also needs to process the HTML, or
at least output the type of processing that is expected
for a given page.
"""

from multiprocessing import Process, Queue, Pool
import urllib2

from cobra.steve.util.prelude import *
from cobra.steve.crawler import fetcher, caches
from cobra.steve.third_party.BeautifulSoup import BeautifulSoup
from cobra.steve.indexing import protokv


def RunGrawler(seed_urls, seed_callback, repos, protokv_file_path):
  output_queue = Queue()
  # reducer = Process(target=OutputProcess, args=(protokv_file_path, output_queue))
  # reducer.start()
  url_queue = Queue()
  processor_pool = Pool()
  for url in seed_urls:
    url_queue.put((url, seed_callback, ()))
  FetchingProcess(url_queue, output_queue, processor_pool, repos)


def FetchingProcess(url_queue, output_queue, processor_pool, repos):
  urls_seen = set()
  def PostProcessCallback(urls, outputs):
    map(url_queue.put, urls)
    map(output_queue.put, outputs)
  while True:
    url = None
    try:
      url, callback, args = url_queue.get()
      if url in urls_seen:
        continue
      urls_seen.add(url)
      html = fetcher.FetchUrl(url, cache_strategy=repos)
      print callback, args
      processor_pool.apply_async(ProcessCallbackWrapper, (callback, url, html), PostProcessCallback)
    except Exception, e:
      PrintStackTrace(url, e)


def ProcessCallbackWrapper(callback, url, html, args=()):
  try:
    soup = BeautifulSoup(html)
    urls = []
    def EmitUrl(url, callback=callback, args=()):
      urls.append((url, callback, args))
    outputs = []
    def Output(key, value):
      outputs.append((key, value))
    callback(url, soup, EmitUrl, Output, *args)
  except Exception, e:
    PrintStackTrace(url, e)
    return [], []
  else:
    return urls, outputs


def OutputProcess(protokv_file_path, output_queue):
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
  type_set = set()
  hashfold = {}
  def Hash(key):
    return str(key)
  try:
    while True:
      key, value = output_queue.get()
      if key is None:
        break
      type_set.add(type(value))
      if len(type_set) > 1:
        print "WARNING: len of type_set > 1.  Set: %s, new type: %s" % (type_set, type(value))
      hashfold.setdefault(Hash(key), protokv_file.MakeNewProto()).MergeFrom(value)
  except KeyboardInterrupt:
    pass
  # If no outputs were made, don't do anything.
  if not type_set:
    return
  print "OutputProcess is cleaning up"
  protokv_file = protokv.ProtoKeyValueFile(type_set.pop(), protokv_file_path, 'w')

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
