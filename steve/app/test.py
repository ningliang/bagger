"""Similiar to app.py, except for unittests.  Also
mirrors all definitions in the python unittest module.
"""

from unittest import *


def run():
  from cobra.steve.app import app
  import unittest
  app.InitializeAndRun(lambda argv: unittest.main())


del main
