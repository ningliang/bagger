"""Basic python application framework.
"""

# Note: you probably can't import the prelude here,
# as that would set up a cyclic dependency?
# from cobra.steve.util.prelude import *


def InitializeAndRun(mainfunc):
  from cobra.steve.app import flags
  flags.DoParse()
  argv = []
  try:
    mainfunc(argv)
  except KeyboardInterrupt:
    print


def run():
  import __main__
  InitializeAndRun(__main__.main)
