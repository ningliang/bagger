"""A very simple, general crawler framework.

To use, inherit from Crawler and implement the appropriate
methods.
"""

from cobra.steve.util.prelude import *
from cobra.steve.crawler import fetcher
from cobra.steve.third_party.BeautifulSoup import *

import urlparse
import traceback

class Crawler(object):
  # TODO(fedele): move this class to cobra.steve.crawler

  def __init__(self, repos, seed_urls):
    self.urls_seen = set()
    self.urls_to_process = []
    self.repos = repos
    self._cur_url = None
    self._cached_data = {}
    self.AddUrls(seed_urls)

  def AddUrls(self, urls):
    """Add multiple urls to be crawled."""
    map(self.AddUrl, urls)

  def AddUrl(self, url):
    """Add a single url to be crawled."""
    if url:
      full_url = urlparse.urljoin(self.CurrentUrl(), url)
      self.urls_to_process.append(full_url)

  def CurrentUrl(self):
    return self._cur_url

  def CacheDataForUrl(self, url, key, value):
    """Associate the (key, value) data pair with the given url.
    These pairs may be retrieved as a dictionary by calling
    GetCachedData.
    """
    self._cached_data.setdefault(url, {})[key] = value

  def GetCachedData(self, url):
    """Retrieve any and all data stored by CacheDataForUrl.  Note that
    this deletes the data from the cache - thus this method may not
    be called more than once with the same url.
    """
    return self._cached_data.pop(url, {})

  def Run(self):
    """Runs the crawler.  Does not return until the entire
    crawl space has been explored.  As such, this may take awhile."""
    while self.urls_to_process:
      url = self.urls_to_process.pop(random.randint(0, len(self.urls_to_process) - 1))
      if url in self.urls_seen:
        continue
      self._cur_url = url
      print >> sys.stderr, "fetching [%-150s]..." % url[:150]
      self.urls_seen.add(url)
      data = fetcher.FetchUrl(url)
      soup = BeautifulSoup(data)
      try:
        self.Process(url, soup)
      except Exception, e:
        traceback.print_exc(file=sys.stderr)

  def Process(self, url, soup):
    """If the given URL is fetched successfully, this method is called as
    a callback.  Implement application specific processing behavior here."""
    raise NotImplementedError
