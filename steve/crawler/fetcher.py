"""Defines methods to make fetching urls easy.

Can also be run as an application - specify a stream of urls
(either on stdin or in a file), and this program will fetch them.
Please note that this does no processing of fetches, and is
simply used to populate the desired cache.  If --urls is
not set, this fetch mode effectively does nothing.
"""

from cobra.steve.util.prelude import *
from cobra.steve.crawler import caches
import urllib2

flags.DefineString("cachedir", None,
                   "The defaultlocal directory to cache http fetches to.  If not specified, no "
                   "default caching is performed.")
flags.DefineString("urls", "-",
                   "The list of urls to extract.  Either a path to a file or '-' "
                   "which specifies that the urls should be read from stdin.  Regardless "
                   "the input should have one url per line.")


_default_cache_strategy = None
def FetchUrl(url, cache_strategy=None):
  # If necessary, initialize the default cache strategy.  We do this
  # on demand rather than at startup because FLAGS is not initialized
  # until the app's main method is called.
  global _default_cache_strategy
  if _default_cache_strategy is None and FLAGS.cachedir:
    _default_cache_strategy = caches.OnDiskCacheStrategy(FLAGS.cachedir)

  # Use the default cache strategy if necessary.
  if cache_strategy is None and _default_cache_strategy is not None:
    cache_strategy = _default_cache_strategy

  # TODO(fedele): we should really normalize the url here.
  if cache_strategy and url in cache_strategy:
    return cache_strategy.get(url)
  else:
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'semantic-searchbot')
    data = urllib2.urlopen(req).read()
    if cache_strategy is not None:
      cache_strategy[url] = data
    return data


def main(argv):
  if FLAGS.urls == '-':
    url_iter = sys.stdin
  else:
    url_iter = open(FLAGS.urls)

  for n, url in enumerate(url_iter):
    url = url.strip()
    if not url:
      continue
    print >> sys.stderr, "fetching url %d (%s)..." % (n, url[:50]),
    start_time = time.time()
    try:
      data = FetchUrl(url)
    except urllib2.HTTPError, e:
      print >> sys.stderr, "error: %s" % e
      continue
    print len(data), time.time() - start_time


if __name__ == '__main__':
  app.run()
