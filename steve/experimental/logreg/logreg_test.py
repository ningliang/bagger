from logreg import *
import unittest

import random


class TestLogisticRegression(unittest.TestCase):
  def testConstant(self):
    for seed in (1337, 666, 8888):
      random.seed(seed)
      xs = [() for n in range(1000)]
      xs_list = AddConstantsToData(xs)
      params = [1.0]
      ys = GenerateRandomVariables(params, xs_list)
      estimated_params = LogisticRegressionParameters(xs_list, ys)
      error = math.sqrt(sum(e * e for e in (g - r for g, r in izip(estimated_params, params))))
      self.assert_(error < 0.10)

  def testSingleParam(self):
    for seed in (1337, 666, 8888):
      random.seed(seed)
      xs = [tuple(int(random.random() < 0.5) for n in range(1))
            for datapoint in range(1000)]
      xs_list = AddConstantsToData(xs)
      params = [-1.0, 0]
      ys = GenerateRandomVariables(params, xs_list)
      estimated_params = LogisticRegressionParameters(xs_list, ys, debug_output=True)
      error = math.sqrt(sum(e * e for e in (g - r for g, r in izip(estimated_params, params))))
      print estimated_params, params
      self.assert_(error < 0.10)




if __name__ == '__main__':
  unittest.main()
  
