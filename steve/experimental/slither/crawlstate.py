"""
Class to maintain the state of a crawl within a sqlite
database.

Ooops... it also became the class to define generic crawl
operations, regardless of crawl progress.

And... it also became the main program.  We should really
factor this better.

TODO(fedele): refactor
"""


from cobra.steve.util.prelude import *
from cobra.steve.experimental.slither import crawlconf

import urllib2
import urlparse
import threading
import Queue
import sqlite3
from sgmllib import SGMLParser


flags.DefineString("crawlname", None, "The root hostname of the site to crawl, e.g. --crawlname=literotica")
flags.DefineInteger("num_workers", 10, "The number of worker threads to use.")
flags.DefineInteger("max_failures", 3, "Maximum number of failures before aborting a url.")
flags.DefineBoolean("use_cache", True, "Whether or not to use a local cache when fetching ")



def EnsureDirectoryExists(dirpath):
  if not os.path.exists(dirpath):
    os.mkdir(dirpath)


class Crawl(object):
  def __init__(self, hostnames, crawldir, seed_urls, db_name="corpus.db"):
    self.hostnames = hostnames
    self._cached_hostids = dict((h, 0) for h in hostnames)
    self._cached_hostnames = {}    
    self.crawldir = crawldir
    self._db_path = os.path.join(self.crawldir, db_name)
    self._html_dir = os.path.join(self.crawldir, "html")    
    self.seed_urls = seed_urls
    EnsureDirectoryExists(self.crawldir)
    EnsureDirectoryExists(self._html_dir)
    
  def MaxFailures(self):
    return FLAGS.max_failures
    
  def IsOnDomain(self, url_pair):    
    hxx, path = url_pair
    return isinstance(hxx, int)

  def MakeCrawlState(self):
    conn = sqlite3.connect(self._db_path)
    conn.text_factory = str
    crawl_state = CrawlState(self, conn, self._cached_hostids)
    self._cached_hostnames = dict((hostid, hostname) for hostname, hostid in self._cached_hostids.iteritems())
    crawl_state.AddUrls(self.seed_urls)
    return crawl_state

  def LocalPath(self, docid):
    """
    Returns a full local path where this crawl should cache
    the given docid.
    """
    return os.path.join(self._html_dir, "%d.html" % docid)

  def ProcessPage(self, docid, base_url, local_path, data):
    ondomain_anchors = []
    offdomain_anchors = []
    for url, text in ExtractAnchorsFromPage(base_url, data):
      url_pair = self.UrlPair(url)
      if self.IsOnDomain(url_pair):
        ondomain_anchors.append((url_pair, text))
      else:
        offdomain_anchors.append((url_pair[0], url_pair[1], text))
    result = CrawlResult(docid, base_url, local_path, ondomain_anchors, offdomain_anchors)
    return result
    
  def UrlPair(self, url):
    o = urlparse.urlparse(url)
    host = o.netloc
    path = o.path + (("?" + o.query) if o.query else '')
    return (self._cached_hostids.get(host, host), path)
    
  def GetUrlFromUrlPair(self, url_pair):
    hostid, path = url_pair
    return urlparse.urljoin("http://" + self._cached_hostnames[hostid], path)

  def HandleTask(self, task):
    docid, url_pair = task
    local_path = self.LocalPath(docid)
    url = self.GetUrlFromUrlPair(url_pair)
    try:      
      data, redirect_url_pair = self.DoFetch(url, local_path)
      if redirect_url_pair is not None:
        return RedirectResult(docid, url, redirect_url_pair)      
      return self.ProcessPage(docid, url, local_path, data)
    except Exception, e:
      import traceback, StringIO
      tb_buffer = StringIO.StringIO()      
      print >> tb_buffer, "Error while processing docid %d url %s" % (docid, url) 
      traceback.print_exc(file=tb_buffer)
      tb = tb_buffer.getvalue()
      # print tb
      tb_buffer.close()
      return ErrorResult(docid, url, error_message=tb)
      
  def DoFetch(self, url, local_path, cache_on_redirect=False):
    """
    Actually performs an HTTP request of the given url.  Returns the response
    data, first caching it to the path given in local_path.  If local_path
    already exists, does not perform an HTTP request but instead uses the
    cached version.
    
    Returns a (data, redirect_url) tuple where data is the fetched content at
    the url and redirect_url is the landing url if there was a redirection,
    or None if there wasn't.
    """
    if FLAGS.use_cache and os.path.exists(local_path):
      data = open(local_path).read()
      return data, None
    else:
      # TODO(fedele): add referrer headers
      # TODO(fedele): user-agent
      # TODO(fedele): handle cookies
      # TODO(fedele): add the ability to fetch compressed
      request = urllib2.Request(url)
      response = urllib2.urlopen(request)
      data = response.read()   
      was_redirect = response.geturl() != url 
      if not was_redirect or cache_on_redirect:
        f = open(local_path, 'w')
        f.write(data)
        f.close()
      return data, self.UrlPair(response.geturl()) if was_redirect else None


      
class CrawlResult(object):
  is_redirect = False

  def __init__(self, docid, url, local_path, ondomain_anchors, offdomain_anchors):
    self.success = True
    self.docid = docid
    self.url = url
    self.local_path = local_path
    self.ondomain_anchors = ondomain_anchors
    self.offdomain_anchors = offdomain_anchors    


class ErrorResult(object):
  is_redirect = False

  def __init__(self, docid, url, error_message):
    self.success = False
    self.docid = docid
    self.url = url
    self.error_message = error_message

    
class RedirectResult(object):
  is_redirect = True

  def __init__(self, docid, url, redirect_url_pair):
    self.success = True
    self.docid = docid
    self.url = url
    self.redirect_url_pair = redirect_url_pair
    

class StatusCounter(object):
  def __init__(self, initial_counts):
    ZeroStatusDict = lambda : dict((k.lower(), v) for k, v in initial_counts.iteritems())
    self._counts = ZeroStatusDict()
    self._old_counts = ZeroStatusDict()
    self.net_timeouts = 0
    self.net_failures = 0
    self.net_complete = 0
    
  def delta(self):
    ret = dict((key, self._counts[key] - self._old_counts[key]) for key in self._counts)
    self._old_counts.update(self._counts)
    return ret
    
  def AddComplete(self, n=1):
    self._counts['complete'] += n
    self._counts['assigned']  -= n
    self.net_complete += n
    
  def AddToCrawl(self, n=1):
    self._counts['tocrawl'] += n
    
  def AddFailed(self, n=1):
    self._counts['failed'] += n
    self.net_failures += n
    
  def AddAborted(self, n=1):
    self._counts['failed'] -= n
    self._counts['aborted'] += n
    
  def AddAssigned(self, n=1):
    self._counts['tocrawl'] -= n
    self._counts['assigned'] += n
    
  def AddRedirect(self, n=1):
    self._counts['assigned'] -= n
    self._counts['redirect'] += n
    
  def AddTimeout(self, n=1):
    self._counts['assigned'] -= n
    self._counts['tocrawl'] += n
    self.net_timeouts += n
  
  def AddFailedRefresh(self, n=1):
    self._counts['failed'] -= n
    self._counts['tocrawl'] += n
    
    

class CrawlState(object):
  def __init__(self, crawl, db_conn, hostids_cache):
    self.crawl = crawl
    self.db_conn = db_conn    
    self._InitializeDatabase(hostids_cache)
    self.counter = StatusCounter(self.StatusCounts())

  def _Cursor(self):
    return self.db_conn.cursor()

  def _Commit(self):
    self.db_conn.commit()

  def _InitializeDatabase(self, hostids_cache):
    c = self._Cursor()
    c.execute("PRAGMA journal_mode=OFF")
    c.execute("PRAGMA synchronous=OFF")
    c.execute("create table if not exists pages (docid integer primary key, hostid integer, url text, local_path text, unique (hostid, url))")
    c.execute("create table if not exists hosts (hostid integer primary key, hostname text unique)")
    c.execute("create table if not exists ondomain_anchors (from_docid integer, to_docid integer, anchor_text text)")
    c.execute("create table if not exists offdomain_anchors (from_docid integer, to_host text, to_path text, anchor_text text)")
    c.execute("create table if not exists crawl (docid integer unique, status text default 'TOCRAWL', num_failures integer default 0, timestamp text)")
    c.execute("create table if not exists errors (docid integer, url text, timestamp text, traceback text)")
    c.execute("create table if not exists ondomain_redirects (from_docid integer, to_docid)")
    c.execute("create table if not exists offdomain_redirects (from_docid integer, to_host text, to_path text)")    
    self._Commit()
    c = self._Cursor()
    hostnames = [(hostname,) for hostname in hostids_cache]        
    c.executemany("insert or ignore into hosts (hostname) values (?)", hostnames)    
    self._Commit()
    c = self._Cursor()
    c.execute("select hostname, hostid from hosts")
    xs = list(c)
    for hostname, hostid in xs:
      hostids_cache[hostname] = hostid    

  def _InsertNewUrl(self, cursor, url_pair):
    """
    Insert the given url into the database, returning its new docid.
    The url must NOT already be in the database.  Also adds the url
    to the to-crawl database if necessary.
    """
    cursor.execute("insert into pages (hostid, url) values (?,?)", url_pair)
    self.counter.AddToCrawl()
    docid = cursor.lastrowid
    cursor.execute("insert into crawl (docid, timestamp) values (?, DATETIME('now'))", (docid,))
    return docid

  def _InsertOnDomainAnchors(self, cursor, from_docid, anchors):
    """
    Helper method to insert ondomain anchors into the database.
    anchors is expected to be a list of (relative_url, anchor_text) pairs.
    """
    url_pairs = map(itemgetter(0), anchors)
    to_docids = self.GetDocids(url_pairs)
    tmp = [(from_docid, to_docid, anchor_text) for to_docid, (url, anchor_text) in izip(to_docids, anchors)]
    cursor.executemany("insert into ondomain_anchors (from_docid, to_docid, anchor_text) values (?,?,?)", tmp)

  def _InsertOffDomainAnchors(self, cursor, from_docid, anchors):
    """
    Helper method to insert offdomain anchors into the database.
    anchors is expected to be a list of (hostname, relative_url, anchor_text) pairs.
    """
    cursor.executemany("insert into offdomain_anchors (from_docid, to_host, to_path, anchor_text) values (%d,?,?,?)" % from_docid, anchors)
    
  def _InsertOnDomainRedirect(self, cursor, from_docid, to_docid):
    cursor.execute("insert into ondomain_redirects (from_docid, to_docid) values (?,?)", (from_docid, to_docid))
    pass

  def _InsertOffDomainRedirect(self, cursor, from_docid, url_pair):
    to_domain, to_path = url_pair
    cursor.execute("insert into offdomain_redirects (from_docid, to_host, to_path) values (?,?,?)", (from_docid, to_domain, to_path))    
  
  def AddUrls(self, urls):
    """
    Add the given set of urls to the to-crawl database, but only if they
    are on domain and weren't already there before.
    """        
    url_pairs = map(self.crawl.UrlPair, urls)    
    ondomain_url_pairs = filter(self.crawl.IsOnDomain, url_pairs)    
    self.GetDocids(ondomain_url_pairs)

  def GetDocids(self, url_pairs, create_docids=True):
    """
    Return a list of docids for the urls.  If create_docids is true,
    creates new docids for any urls that don't have them (and thus
    creates corresponding entries in the pages table).  Otherwise,
    returns None for urls without docids.
    """
    c = self._Cursor()
    docids = []
    for url_pair in url_pairs:
      hostid = 0
      c.execute("select docid from pages where hostid=? and url=?", url_pair)
      xs = list(c)
      if len(xs) == 0:
        if create_docids:
          docid = self._InsertNewUrl(c, url_pair)
        else:
          docid = None
      else:
        docid = xs[0][0]
      docids.append(docid)
    self._Commit()
    return docids

  def GetDocid(self, url_pair, create_docids=True):
    """
    Similar to GetDocids, except it only takes a single url_pair, and
    it always returns a docid, even for urls that don't exist yet.
    """
    docids = self.GetDocids([url_pair], create_docids)
    return docids[0]

  def GetTaskAssignment(self, num_to_assign):
    """
    Returns a list of up to the requested num_to_assign (docid, url)
    pairs, each one previously unassigned.  Updates their crawl
    statuses to assigned.
    """
    c = self._Cursor()
    c.execute("""select crawl.docid, hostid, url from crawl, pages
                 where crawl.docid=pages.docid and
                 crawl.status='TOCRAWL' limit %d""" % num_to_assign)
    docids_and_url_pairs = [(docid, (hostid, url)) for docid, hostid, url in c]    
    docids = [(docid,) for docid, url_pair in docids_and_url_pairs]
    c.executemany("update crawl set status='ASSIGNED', timestamp=DATETIME('now') where docid=?", docids)
    self._Commit()
    self.counter.AddAssigned(len(docids_and_url_pairs))
    return docids_and_url_pairs

  def SubmitTaskResult(self, result):
    """
    After processing a fetch assignment, call this method to
      1) update the document's local path
      2) insert the given anchors into the anchors tables
      3) add previously unseen urls to the crawl pipeline.
    """    
    c = self._Cursor()
    if result.success:
      if result.is_redirect:
        self.counter.AddRedirect()
        url_pair = result.redirect_url_pair
        if self.crawl.IsOnDomain(url_pair):
          docid = self.GetDocid(url_pair)
          self._InsertOnDomainRedirect(c, result.docid, docid)
        else:
          self._InsertOffDomainRedirect(c, result.docid, url_pair)
        c.execute("update crawl set status='REDIRECT', timestamp=DATETIME('now') where docid=?", (result.docid,))
      else:
        self.counter.AddComplete()
        self._InsertOnDomainAnchors(c, result.docid, result.ondomain_anchors)
        self._InsertOffDomainAnchors(c, result.docid, result.offdomain_anchors)
        local_path_relative_to_db = "html/%d.html" % result.docid  # TODO(fedele): don't hardcode this
        c.execute("update crawl set status='COMPLETE', timestamp=DATETIME('now') where docid=?", (result.docid,))
        c.execute("update pages set local_path=? where docid=?", (local_path_relative_to_db, result.docid))
    else:
      self.counter.AddFailed()
      c.execute("update crawl set status='FAILED', timestamp=DATETIME('now'), num_failures=num_failures+1 where docid=?", (result.docid,))
      c.execute("insert into errors (docid, url, timestamp, traceback) values (?,?,DATETIME('now'),?)", (result.docid, result.url, result.error_message))      
    self._Commit()

  def CleanUpTimedOutAssignments(self, timeout):
    """
    Changes the status of any crawl assignment that has been
    assigned for more than timeout seconds so that it can
    be reassigned.  Also, sets the status of urls that have
    failed too many times to "ABORTED".
    """
    c = self._Cursor()
    c.execute("update crawl set status='ABORTED', timestamp=DATETIME('now') where status='FAILED' and num_failures > %d" % crawl.MaxFailures())    
    self.counter.AddAborted(c.rowcount)
    c.execute("update crawl set status='TOCRAWL', timestamp=DATETIME('now'), num_failures=num_failures+1 where status='ASSIGNED' and timestamp < datetime('now', '-%d seconds')" % timeout)
    self.counter.AddTimeout(c.rowcount)
    c.execute("update crawl set status='TOCRAWL', timestamp=DATETIME('now') where status='FAILED' and timestamp < datetime('now', '-%d seconds')" % timeout)
    self.counter.AddFailedRefresh(c.rowcount)
    self._Commit()
    
  ALL_STATUSES = ("ASSIGNED", "COMPLETE", "FAILED", "REDIRECT", "TOCRAWL", "ABORTED")

  def StatusCounts(self):
    """
    does not Returns a string
    """
    c = self._Cursor()
    c.execute("select status, count(*) from crawl group by status")
    counts = dict((s, 0) for s in self.ALL_STATUSES)
    counts.update(dict(c))
    return counts
    
  def DocsCachedLocallyIter(self):
    c = self._Cursor()
    c.execute("select docid, url from pages where local_path != ''")
    return ((docid, url, self.crawl.LocalPath(docid)) for docid, url in c)


class AnchorExtractingParser(SGMLParser):
  def __init__(self, base_url, *args, **kwargs):
    self.base_url = base_url
    SGMLParser.__init__(self, *args, **kwargs)

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
      self.href = urlparse.urljoin(self.base_url, hrefs[0])
      self.in_anchor = True
      self.anchor_text = ''

  def end_a(self):
    if self.in_anchor:
      self.anchors.append((self.href, self.anchor_text))
      self.ExitAnchor()

  def handle_data(self, data):
    if self.in_anchor:
      self.anchor_text += data.strip()


def ExtractAnchorsFromPage(base_url, data):
  """
  Return a list of (url, anchor_text) pairs representing
  all anchors on the given html page.
  """
  parser = AnchorExtractingParser(base_url)
  parser.feed(data)
  parser.close()
  return parser.anchors


def WorkerThreadMain(crawl, task_queue, result_queue):
  while True:
    # Get a task, handle it, and then post the result.
    result_queue.put(crawl.HandleTask(task_queue.get()))



def SchedulerThreadMain(crawl, task_queue, result_queue):
  check_every_interval        = 1
  target_task_queue_size      = 600
  task_queue_refill_threshold = 250  
  no_sleep_threshold          = 2500

  crawl_state = crawl.MakeCrawlState()
  
  # Remove any currently pending urls that exist at the start
  # of a crawl - they're probably leftovers from a previous run.
  crawl_state.CleanUpTimedOutAssignments(0)  
  
  crawl_start_time = time.time()

  while True:
    # Process completed results for as long as we can...
    # TODO: batch anchors up and insert them at the end
    #       remember how long it takes to insert how many
    #       and stop reading if it looks like the projected time will exceed the alloted interval
    #       we can remember if we were over/under the projection last time and adjust the rate accordingly    
    n = 0
    start_time = time.time()
    try:
      while time.time() - start_time < check_every_interval:
        result = result_queue.get_nowait()
        crawl_state.SubmitTaskResult(result)        
        n += 1
    except Queue.Empty:
      pass
    insert_time_taken = time.time() - start_time
    num_pending = result_queue.qsize()    

    # Cleanup any assignments that have timed out.    
    crawl_state.CleanUpTimedOutAssignments(60 * 3)

    # Put new tasks into the task_queue.    
    if task_queue.qsize() < task_queue_refill_threshold:
      number_to_assign = target_task_queue_size - task_queue.qsize()
      tasks = crawl_state.GetTaskAssignment(number_to_assign)      
      for task in tasks:
        task_queue.put(task)
    
    update_time_taken = time.time() - start_time

    # counts = crawl_state.StatusCounts()
    counts = crawl_state.counter._counts
    net_complete = crawl_state.counter.net_complete   
    current_time = time.time() - crawl_start_time
    crawl_rate = net_complete / (current_time or 1)
    
    template = "%8.2f seconds: %7d processed (insert=%5.2fs total=%5.2fs) %5d pending -- %9d complete, %9d tocrawl, %5d failed -- net rate: %6.2f"    
    args = (current_time, n, insert_time_taken, update_time_taken, num_pending, counts['complete'], counts['tocrawl'], counts['failed'], crawl_rate)    
    print template % args
    
    # Go to sleep!
    if num_pending < no_sleep_threshold:
      time.sleep(check_every_interval)

      
def CrawlFromFlags():  
  assert FLAGS.crawlname is not None, "please specify a name for this crawl via the --crawlname flag"
  crawlname = FLAGS.crawlname
  master = crawlconf.LoadCrawlMaster()
  hostnames = master.GetHostNames(crawlname)
  seed_urls = master.GetSeedUrls(crawlname)  
  crawldir = master.GetCrawlDir(crawlname)
  host_roots = ["http://" + h for h in hostnames]  
  seed_urls.extend(host_roots)
  return Crawl(hostnames, crawldir, seed_urls)
  

def CrawlStateFromFlags():
  crawl = CrawlFromFlags()
  return crawl, crawl.MakeCrawlState()


def main(argv):  
  crawl = CrawlFromFlags()  
  task_queue = Queue.Queue()
  result_queue = Queue.Queue()

  worker_args = (crawl, task_queue, result_queue)
  workers = []
  for n in range(FLAGS.num_workers):
    worker = threading.Thread(target=WorkerThreadMain, args=worker_args)
    worker.daemon = True
    worker.start()
    workers.append(worker) 

  SchedulerThreadMain(*worker_args)



if __name__ == '__main__':
  app.run()
