"""


"""

import shutil

from cobra.steve.util.prelude import *


class LocalRepository(object):
  def __init__(self, root_dir, delete_existing_repos=False):
    if delete_existing_repos:
      shutil.rmtree(root_dir)
    self.root_dir = root_dir
    if not os.path.exists(self.root_dir):
      os.mkdir(self.root_dir)
    resources_dir = os.path.join(self.root_dir, "resources/")
    if not os.path.exists(resources_dir):
      os.mkdir(resources_dir)

  def AddPurchasePoint(self, purchase_point):
    repos_file_path = os.path.join(self.root_dir, "resources/handbag-%s" % purchase_point.CanonicalId())
    if os.path.exists(repos_file_path):
      mode = 'a'  # Append to file if it exists.
    else:
      mode = 'w'  # (Over)write otherwise
    f = open(repos_file_path, mode)
    purchase_point.WriteToOpenFile(f)
    f.close()
