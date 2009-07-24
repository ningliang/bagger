import os


def ExtractCobraDir(filepath):
  "Given filepath, try to find the cobra root directory within it."
  COBRA = 'cobra'
  n = filepath.find(COBRA) + len(COBRA) + 1
  basedir = filepath[:n]
  assert os.path.exists(basedir) and os.path.isdir(basedir), "basedir '%s' (inferred from '%s') is not a valid directory" % (basedir, proto_filepath)
  return basedir


def CobraDir():
  """Return an absolute path to the cobra directory under which this
  script is running."""
  return ExtractCobraDir(os.getcwd())
