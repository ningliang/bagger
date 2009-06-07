from cobra.steve.util.prelude import *

import UserDict
import urllib


def FilenameToUrl(filename):
  """Used by OnDiskCacheStrategy to convert a filename into a url."""
  return urllib.unquote_plus(filename)

def UrlToFilename(url):
  """Used by OnDiskCacheStrategy to convert a url into a local filename."""
  return urllib.quote_plus(url)


class InMemoryCacheStrategy(dict):
  """A simple in-memory cache strategy based on a python dictionary."""
  def __str__(self):
    return repr(self)


class OnDiskCacheStrategy(UserDict.DictMixin):
  """A simple on-disk cache."""
  def __init__(self, on_disk_directory):
    if not os.path.exists(on_disk_directory):
      os.mkdir(on_disk_directory)
    elif os.path.isdir(on_disk_directory):
      # The directory already exists, great.
      pass
    else:
      # It exists but isn't a directory - abortz!
      raise ValueError, "cache-directory '%s' exists but is a file!"
    self._dir = on_disk_directory

  def __str__(self):
    return "<OnDiskCacheStrategy in '%s'>" % self._dir

  def __getitem__(self, key):
    path = self.KeyToPath(key)
    if os.path.exists(path):
      return open(path).read()
    else:
      raise KeyError

  def __setitem__(self, key, data):
    open(self.KeyToPath(key), 'w').write(data)

  def keys(self):
    return map(self.PathToKey, glob.glob(os.path.join(self._dir, "*")))

  def __contains__(self, key):
    return os.path.exists(self.KeyToPath(key))

  def KeyToPath(self, key):
    "Translate key into an absolute file path."
    return os.path.join(self._dir, UrlToFilename(key))

  def PathToKey(self, path):
    """Take an absolute or relative path and return the key
    it represents.  Raises a ValueError if path does not
    represent a valid key.
    """
    return FilenameToUrl(os.path.basename(path))
