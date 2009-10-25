from cobra.steve.util.prelude import *

import ConfigParser
import sqlite3


flags.DefineString("config_file", ".crawlconf", "Name of the local slither config file")


class CrawlMaster(object):
  """
  Stores all local information about the crawl, such as directories,
  database connection parameters, seed urls, crawlnames, etc.
  """
  def __init__(self, config):
    """
    @config - an object of type ConfigParser    
    """
    self.config = config
    self.basedir = config.get('base', 'basedir')
    
  def GetCrawlDir(self, crawlname):
    return os.path.join(self.basedir, crawlname)
    
  def GetHostNames(self, crawlname):
    return filter(None, self.config.get(crawlname, 'hosts').split())
    
  def GetSeedUrls(self, crawlname):
    return filter(None, self.config.get(crawlname, 'seeds').split())


def ParentDirectoryIter(start_dir):
  curdir = start_dir
  while True:
    yield curdir
    new_curdir = os.path.dirname(curdir)
    if new_curdir == curdir:
      raise StopIterationException
    curdir = new_curdir

    
class ConfigFileNotFoundError(Exception):
  pass


def LoadCrawlMaster(config_filename=None):
  filename = config_filename or FLAGS.config_file
  for dirname in ParentDirectoryIter(os.getcwd()):
    possible_config_path = os.path.join(dirname, filename)
    if os.path.exists(possible_config_path):
      return LoadCrawlMasterFileFromPath(possible_config_path)
  else:
    raise ConfigFileNotFoundError
      
      
def LoadCrawlMasterFileFromPath(filepath):
  config = ConfigParser.RawConfigParser()
  config.read(filepath)
  return CrawlMaster(config)
  
  