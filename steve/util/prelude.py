"""Methods to make functional programming easier in Python.

This module is intended to be imported like follows:

from steve.util.prelude import *

Also imports many commonly used modules, which would
especially be useful for quick scripts.
"""

__author__ = 'stephen.fedele@gmail.com (Stephen Fedele)'

# Basic functionality that is always necessary.
import os
import sys
import re
import glob
import random
import time
import math
import copy

# Some more cobra.steve specific common imports.
from cobra.steve.app import app, flags
FLAGS = flags.FLAGS

# These are for a more functional style.
from itertools import *
from operator import itemgetter


def any(iterable):
  for x in iterable:
    if x:
      return True
  return False


def all(iterable):
  for x in iterable:
    if not x:
      return False
  return True


def mean(iterable):
  total = 0.0
  n = 0
  for x in iterable:
    total += x
    n += 1
  return n and total / n or 0

# TODO(fedele): other aggregators:
#   count
#   gaussian
#   exponential
#   binomial
#   top
#   examples
#   sorted


def groupby_(iterable, keyfunc):
  """
  Automatically handle the intermediate sorting step in the groupby.
  You could imagine this as the intermediary step in a map-reduce.
  """
  # TODO(fedele): this should ALSO ideally turn the iterators
  # fed to the subsequent functions into something more useable,
  # e.g. do the list slurping here ourselves.
  return groupby(sorted(iterable, key=keyfunc), keyfunc)


def groupby_strict(iterable, keyfunc):
  """
  This is the same as groupby_ except that it caches the result.
  This lets you iterate multiple times over the returned iterable.
  Note: this may take significant auxillary storage.
  """
  return map((id | list), groupby_(iterable, keyfunc))


class ComposableFunction(object):
  """
  A little wrapper around function objects that allows you
  to use a operators to compose functions.  These are
  properly called functors, and they make expressing
  functional pipelines via itertools a LOT easier.

  Some defining examples:

  >>> (x, y) = ('x', 'y')

  >>> (F | G)((x, y))
  (F(x), G(y))

  >>> (F ** G)('x')
  (F(x), F(x))

  >>> (F >> G)('x')
  G(F(x))

  >>> (F << G)('x')
  F(G(x))
  """

  def __init__(self, func):
    self.func = func

  def __call__(self, *args, **kwargs):
    return self.func(*args, **kwargs)

  def __or__(self, other):
    """
    (self | other)((x, y)) = (self(x), other(y))
    """
    return lambda (x, y): (self(x), other(y))

  def __ror__(self, other):
    """
    (other | self)((x, y)) = (other(x), self(y))
    """
    return lambda (x, y): (other(x), self(y))

  def __pow__(self, other):
    """
    (self ** other)(x) = (self(x), other(x))
    """
    return lambda x: (self(x), other(x))

  def __rpow__(self, other):
    """
    (other ** self)(x) = (other(x), self(x))
    """
    return lambda x: (other(x), self(x))

  def __lshift__(self, other):
    """
    (self << other)(x) = self(other(x))
    """
    return lambda x: self(other(x))

  def __rshift__(self, other):
    """
    (self >> other)(x) = other(self(x))
    """
    return lambda x: other(self(x))

  def __rlshift__(self, other):
    """
    (other << self)(x) = other(self(x))
    """
    return lambda x: other(self(x))

  def __rrshift__(self, other):
    """
    (other >> self)(x) = self(other(x))
    """
    return lambda x: self(other(x))


def c(func):
  """
  Turn func into a composable function.  Analogous to lift in Haskell.
  """
  return ComposableFunction(func)


id = c(lambda x: x)

def const(f):
  """
  Every time this function is evaluated, evaluate and return the
  result of f.  Useful for wrapping random.random() or similar.
  """
  return lambda : f()


def itemgetters(*args):
  """
  Helper function that extracts a tuple of indices from a record.
  Returns a ComposableFunction.
  """
  return c(lambda r: map(r.__getitem__, args))


def itemgetter(x):
  """
  A ComposableFunction wrapper around operator.itemgetter
  """
  import operator
  return c(operator.itemgetter(x))


# A few classes that are useful in examples of
# the above functors.
class _Base(object):
  def __init__(self, *args):
    self.x = args and args[0] or ''
  def __str__(self):
    return "%s(%s)" % (self.label, self.x)
  def __repr__(self):
    return str(self)

class F_(_Base):
  label = "F"
F = c(F_)

class G_(_Base):
  label = "G"
G = c(G_)


# Almost all of the following methods are taken verbatim
# from the 'Recipes' section on http://docs.python.org/library/itertools.html

def take(n, iterable):
  "Return first n items of the iterable as a list"
  return list(islice(iterable, n))

def enumerate(iterable, start=0):
  return izip(count(start), iterable)

def tabulate(function, start=0):
  "Return function(0), function(1), ...."
  return imap(function, count(start))

def consume(iterable, n):
  "Advance the iterator n-steps ahead.  If n is none, consume entirely."
  # TODO(fedele): note that itertools recipe is _different_ here, and uses
  # collections.deque with a maxlen parameter.  Since this feature was
  # only added in python2.6, we can't use it here.  Lame!
  for x in islice(iterable, n):
    pass

def slurp(iterable):
  return consume(iterable, None)


def timeit(f, *args, **kwargs):
  start_time = time.time()
  ret = f(*args, **kwargs)
  return (time.time() - start_time, ret)


def main():
  print F   ()
  print G   ()
  print F(G())
  print G(F())
  print (G ** F)  ()

  print (G << c(F))  ()
  print (G >> c(F))  ()
  print (c(G) << F)  ()
  print (c(G) >> F)  ()



if __name__ == '__main__':
  main()
