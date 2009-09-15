# Inspired by http://www.cdc.noaa.gov/people/jeffrey.s.whitaker/python/logistic_regression.py

import numpy as np

def LogisticRegression(x, y, beta_start=None, verbose=False,
                       convergance_threshold=1e-3, max_iterations=500):
  if x.shape[-1] != len(y):
    raise ValueError, "x.shape[-1] and y should be the same length"
  try:
    N, npreds = x.shape[1], x.shape[0]
  except:
    N, npreds = x.shape[-1], 1

  if beta_start is None:
    beta_start = np.zeros(npreds+1, x.dtype)
  X = np.ones((npreds + 1, N), x.dtype)
  X[1:, :] = x  # 0th row is for the constants
  Xt = np.transpose(X)

  diff = 1.0
  beta = beta_start
  if verbose:
    print "iteration beta log-likelihood |beta - beta_old|"
  for iteration in xrange(max_iterations):
    beta_old = beta
    ebx = np.exp(np.dot(beta, X))
    p = ebx / (1 + ebx)
    l = np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))     # Log-Likelihood
    s = np.dot(X, y - p)                                    # Scoring function.
    J_bar = np.dot(X * p, Xt)                               # Information matrix.
    beta = beta_old + np.dot(np.linalg.inv(J_bar), s)
    diff = np.sum(np.fabs(beta - beta_old))                 # Sum of absolute differences.
    if verbose:
      print iteration + 1, beta, l, diff
    if diff <= convergance_threshold:
      break
  else:
    print 'warning: convergance not achieved with threshold of %s in %s iterations' % (convergance_threshold,
                                                                                       max_iterations)
  return beta, J_bar, l


def calcprob(beta, x):
  """
  calculate probabilities (in percent) given beta and x
  """
  try:
    N, npreds = x.shape[1], x.shape[0]
  except: # single predictor, x is a vector, len(beta)=2.
    N, npreds = len(x), 1
  if len(beta) != npreds + 1:
    raise ValueError,'sizes of beta and x do not match!'
  X = np.ones((npreds + 1,N), x.dtype)
  X[1:, :] = x
  ebx = np.exp(np.dot(beta, X))
  return ebx /(1 + ebx)
