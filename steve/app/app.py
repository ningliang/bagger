"""Basic python application framework.
"""

# Note: you probably can't import the prelude here,
# as that would set up a cyclic dependency?
# from cobra.steve.util.prelude import *



def run():
  from cobra.steve.app import flags
  import __main__
  flags.DoParse()
  argv = []
  try:
    __main__.main(argv)
  except KeyboardInterrupt:
    print
