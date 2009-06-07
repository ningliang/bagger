"""Methods to make app-level global definition of flags easy.

TODO(fedele): write example usage.
"""

__author__ = 'stephen.fedele@gmail.com (Stephen Fedele)'

# Note: you probably can't import the prelude here,
# as that would set up a cyclic dependency?
# from cobra.steve.util.prelude import *

import optparse
import re


class FlagParser(object):
  def __init__(self):
    self.parser = optparse.OptionParser()
    self.options = None
    self.args = None

  def _DoParse(self):
    self.options, self.args = self.parser.parse_args()

  def __getattr__(self, attr):
    if attr.startswith("Define"):
      raise AttributeError, "Use 'flags.%s' instead of 'FLAGS.%s'" % (attr, attr)
    return getattr(self.options, attr)

  def _Define(self, value_type, flag_name, default, description):
    # TODO(fedele): output a reasonable error message here
    assert re.match(r'^[-A-Za-z]+$', flag_name)
    self.parser.add_option("--%s" % flag_name,
                           dest=flag_name,
                           default=default,
                           help=description,
                           type=value_type)

  def _DefineString(self, *args, **kwargs):
    self._Define("string", *args, **kwargs)

  def _DefineInteger(self, *args, **kwargs):
    self._Define("int", *args, **kwargs)

  def _DefineFloat(self, *args, **kwargs):
    self._Define("float", *args, **kwargs)

  def _DefineBoolean(self, flag_name, default, description):
    # TODO(fedele): output a reasonable error message here
    assert re.match(r'^[-A-Za-z]+$', flag_name)
    true_name = "--%s" % flag_name
    false_name = "--no%s" % flag_name
    self.parser.add_option(true_name, action="store_true", dest=flag_name,
                           help=description)
    self.parser.add_option(false_name, action="store_false", dest=flag_name,
                           default=default)


FLAGS = FlagParser()
DefineBoolean  = FLAGS._DefineBoolean
DefineString   = FLAGS._DefineString
DefineInteger  = FLAGS._DefineInteger
DefineFloat    = FLAGS._DefineFloat
DoParse        = FLAGS._DoParse
