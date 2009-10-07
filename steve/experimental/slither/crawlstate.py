"""
Class to maintain the state of a crawl within a sqlite
database.
"""

from cobra.steve.util.prelude import *

import urllib2
import urlparse
import threading
import Queue
import sqlite3
from sgmllib import SGMLParser


class CrawlResult(object):
  def __init__(self, docid, local_path, ondomain_anchors, offdomain_anchors):
    self.success = True
    self.docid = docid
    self.local_path = local_path
    self.ondomain_anchors = ondomain_anchors
    self.offdomain_anchors = offdomain_anchors


class ErrorResult(object):
  def __init__(self, docid, error_message):
    self.success = False
    self.docid = docid
    self.error_message = error_message


def EnsureDirectoryExists(dirpath):
  if not os.path.exists(dirpath):
    os.mkdir(dirpath)


class Crawl(object):
  def __init__(self, host, crawldir, db_name="corpus.db"):
    self.host = host
    self._http_host = "http://%s" % host
    self.crawldir = crawldir
    EnsureDirectoryExists(self.crawldir)
    self._db_path = os.path.join(self.crawldir, db_name)
    self._html_dir = os.path.join(self.crawldir, "html")
    EnsureDirectoryExists(self._html_dir)

  def AbsoluteUrl(self, possibly_relative_url):
    """
    Given a url found on a page on host, return the absolute
    url it refers to.  This may take a relative url like '/index.html'
    on 'foobar.com' and return 'http://foobar.com/index.html' -
    if given a url like 'http://baz.org/index.html' while crawling
    'foobar.com', will return 'http://baz.org/index.html'
    """
    return urlparse.urljoin(self._http_host, possibly_relative_url)

  def SplitUrl(self, absolute_url):
    """
    Given a url, returns a tuple of (offdomain_host, path) where
    offdomain_host is None if the url is ondomain.
    """
    o = urlparse.urlparse(absolute_url)
    path = o.path
    if o.query:
      path += "?" + o.query
    if o.netloc == self.host:
      return None, path
    else:
      return o.netloc, path

  def MakeCrawlState(self):
    conn = sqlite3.connect(self._db_path)
    conn.text_factory = str
    return CrawlState(self, conn)

  def LocalPath(self, docid):
    """
    Returns a full local path where this crawl should cache
    the given docid.
    """
    return os.path.join(self._html_dir, "%d.html" % docid)

  def ProcessPage(self, docid, url, local_path, data):
    anchors = [(self.SplitUrl(self.AbsoluteUrl(url)), text) for url, text in ExtractAnchorsFromPage(data)]
    ondomain_anchors = [(path, text) for ((offdomain, path), text) in anchors if offdomain is None]
    offdomain_anchors = [(offdomain, path, text) for ((offdomain, path), text) in anchors if offdomain is not None]
    result = CrawlResult(docid, local_path, ondomain_anchors, offdomain_anchors)
    return result

  def HandleTask(self, task):
    docid, url = task
    local_path = self.LocalPath(docid)
    try:
      data = DoFetch(url, local_path)
      return self.ProcessPage(docid, url, local_path, data)
    except Exception, e:
      print >> sys.stderr, "ERROR", e
      import traceback
      traceback.print_exc(file=sys.stdout)
      return ErrorResult(docid, error_message=str(e))


class CrawlState(object):
  def __init__(self, crawl, db_conn):
    self.crawl = crawl
    self.db_conn = db_conn
    self._InitializeDatabase()

  def _Cursor(self):
    return self.db_conn.cursor()

  def _Commit(self):
    self.db_conn.commit()

  def _InitializeDatabase(self):
    c = self._Cursor()
    c.execute("create table if not exists pages (docid integer primary key, url text unique, local_path text)")
    c.execute("create table if not exists ondomain_anchors (from_docid integer, to_docid integer, anchor_text text)")
    c.execute("create table if not exists offdomain_anchors (from_docid integer, to_host text, to_path text, anchor_text text)")
    c.execute("create table if not exists crawl (docid integer unique, status text default 'TOCRAWL', num_failures integer default 0, timestamp text)")
    self._Commit()

  def _InsertNewUrl(self, cursor, url):
    """
    Insert the given url into the database, returning its new docid.
    The url must NOT already be in the database.  Also adds the url
    to the to-crawl database if necessary.
    """
    cursor.execute("insert into pages (url) values (?)", (url,))
    docid = cursor.lastrowid
    cursor.execute("insert or ignore into crawl (docid, timestamp) values (?, DATETIME('now'))", (docid,))
    return docid

  def _InsertOnDomainAnchors(self, cursor, from_docid, anchors):
    """
    Helper method to insert ondomain anchors into the database.
    anchors is expected to be a list of (relative_url, anchor_text) pairs.
    """
    urls = map(itemgetter(0), anchors)
    to_docids = self.GetDocids(urls, create_docids=True)
    tmp = [(from_docid, to_docid, anchor_text) for to_docid, (url, anchor_text) in izip(to_docids, anchors)]
    cursor.executemany("insert into ondomain_anchors (from_docid, to_docid, anchor_text) values (?,?,?)", tmp)

  def _InsertOffDomainAnchors(self, cursor, from_docid, anchors):
    """
    Helper method to insert offdomain anchors into the database.
    anchors is expected to be a list of (hostname, relative_url, anchor_text) pairs.
    """
    cursor.executemany("insert into offdomain_anchors (from_docid, to_host, to_path, anchor_text) values (%d,?,?,?)" % from_docid, anchors)

  def AddUrls(self, urls):
    """
    Add the given set of on-domain anchors to the to-crawl database,
    if they aren't already there.
    """
    relative_paths = map(itemgetter(1), ifilterfalse(itemgetter(0), imap(self.crawl.SplitUrl, urls)))
    self.GetDocids(relative_paths, create_docids=True)

  def GetDocids(self, urls, create_docids=False):
    """
    Return a list of docids for the urls.  If create_docids is true,
    creates new docids for any urls that don't have them (and thus
    creates corresponding entries in the pages table).  Otherwise,
    returns None for urls without docids.
    """
    c = self._Cursor()
    docids = []
    for url in urls:
      c.execute("select docid from pages where url=?", (url,))
      xs = list(c)
      if len(xs) == 0:
        if create_docids:
          docid = self._InsertNewUrl(c, url)
        else:
          docid = None
      else:
        docid = xs[0][0]
      docids.append(docid)
    self._Commit()
    return docids

  def GetDocid(self, url):
    """
    Similar to GetDocids, except it only takes a single url, and
    it always returns a docid, even for urls that don't exist yet.
    """
    docids = self.GetDocids([url], create_docids=True)
    return docids[0]

  def GetTaskAssignment(self, num_to_assign):
    """
    Returns a list of up to the requested num_to_assign (docid, url)
    pairs, each one previously unassigned.  Updates their crawl
    statuses to assigned.
    """
    c = self._Cursor()
    c.execute("""select crawl.docid, url from crawl, pages
                 where crawl.docid=pages.docid and
                 crawl.status='TOCRAWL' limit %d""" % num_to_assign)
    docids_and_urls = list(c)
    docids = [(docid,) for docid, url in docids_and_urls]
    c.executemany("update crawl set status='ASSIGNED', timestamp=DATETIME('now') where docid=?", docids)
    self._Commit()
    return [(docid, self.crawl.AbsoluteUrl(url)) for docid, url in docids_and_urls]

  def SubmitTaskResult(self, result):
    """
    After processing a fetch assignment, call this method to
      1) update the document's local path
      2) insert the given anchors into the anchors tables
      3) add previously unseen urls to the crawl pipeline.
    """
    c = self._Cursor()
    if result.success:
      self._InsertOnDomainAnchors(c, result.docid, result.ondomain_anchors)
      self._InsertOffDomainAnchors(c, result.docid, result.offdomain_anchors)
      local_path_relative_to_db = "html/%d.html" % result.docid  # TODO(fedele): don't hardcode this
      c.execute("update crawl set status='COMPLETE', timestamp=DATETIME('now') where docid=?", (result.docid,))
      c.execute("update pages set local_path=? where docid=?", (local_path_relative_to_db, result.docid))
    else:
      c.execute("update crawl set status='FAILED', timestamp=DATETIME('now'), num_failures=num_failures+1 where docid=?", (result.docid,))
      # TODO(fedele): insert the result's error message into some sort of error table so we can track them.
    self._Commit()

  def CleanUpTimedOutAssignments(self, timeout):
    """
    Changes the status of any crawl assignment that has been
    assigned for more than timeout seconds so that it can
    be reassigned.  Also, sets the status of urls that have
    failed too many times to "ABORTED".
    """
    c = self._Cursor()
    c.execute("update crawl set status='TOCRAWL' where (status='ASSIGNED' or status='FAILED') and timestamp < datetime('now', '-%d seconds')" % timeout)
    # TODO(fedele): set to 'ABORTED' any page that has num_failures > max
    self._Commit()


def DoFetch(url, local_path):
  """
  Actually performs an HTTP request of the given url.  Returns the response
  data, first caching it to the path given in local_path.  If local_path
  already exists, does not perform an HTTP request but instead uses the
  cached version.
  """
  if os.path.exists(local_path):
    data = open(local_path).read()
  else:
    data = urllib2.urlopen(url).read()
    f = open(local_path, 'w')
    f.write(data)
    f.close()
  return data


def EmptyQueueNonBlocking(queue):
  """
  Helper function - returns an iterator over all current items
  in a queue, removing them as it goes.  The iterator ends when
  there are no more items immediately available in the queue.
  """
  try:
    while True:
      yield queue.get_nowait()
  except Exception, e:
    pass


class AnchorExtractingParser(SGMLParser):
  def reset(self):
    SGMLParser.reset(self)
    self.anchors = []
    self.ExitAnchor()

  def ExitAnchor(self):
    self.in_anchor = False
    self.anchor_text = None
    self.href = None

  def start_a(self, attrs):
    hrefs = [v for k, v in attrs if k == 'href']
    if hrefs:
      self.href = hrefs[0]
      self.in_anchor = True
      self.anchor_text = ''

  def end_a(self):
    if self.in_anchor:
      self.anchors.append((self.href, self.anchor_text))
      self.ExitAnchor()

  def handle_data(self, data):
    if self.in_anchor:
      self.anchor_text += data.strip()


def ExtractAnchorsFromPage(data):
  """
  Return a list of (url, anchor_text) pairs representing
  all anchors on the given html page.
  """
  parser = AnchorExtractingParser()
  parser.feed(data)
  parser.close()
  return parser.anchors


def WorkerThreadMain(crawl, task_queue, result_queue):
  while True:
    # Get a task, handle it, and then post the result.
    result_queue.put(crawl.HandleTask(task_queue.get()))


def SchedulerThreadMain(crawl, task_queue, result_queue):
  check_every_interval = 1
  number_to_assign     = 100
  crawl_state = crawl.MakeCrawlState()
  # Remove any currently pending urls that exist at the start
  # of a crawl - they're probably leftovers from a previous run.
  crawl_state.CleanUpTimedOutAssignments(0)
  while True:
    # Process completed results.
    n = 0
    for result in EmptyQueueNonBlocking(result_queue):
      n += 1
      crawl_state.SubmitTaskResult(result)
    print >> sys.stderr, "processed %d results" % n
    # Cleanup any assignments that have timed out.
    crawl_state.CleanUpTimedOutAssignments(60 * 3)
    # Put new tasks into the task_queue.
    if task_queue.qsize() < number_to_assign:
      tasks = crawl_state.GetTaskAssignment(number_to_assign)
      print >> sys.stderr, "got %d new tasks!" % len(tasks)
      for task in tasks:
        task_queue.put(task)
    # Go to sleep!
    time.sleep(check_every_interval)


def main(argv):
  crawl = Crawl('delicious.com', '/tmp/crawls/delicious_com')
  task_queue = Queue.Queue()
  result_queue = Queue.Queue()

  worker_args = (crawl, task_queue, result_queue)
  workers = []
  for n in range(10):
    worker = threading.Thread(target=WorkerThreadMain, args=worker_args)
    worker.daemon = True
    worker.start()
    workers.append(worker)

  crawl_state = crawl.MakeCrawlState()
  crawl_state.AddUrls(["/"])

  SchedulerThreadMain(*worker_args)



if __name__ == '__main__':
  app.run()
