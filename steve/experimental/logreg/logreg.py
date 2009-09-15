from itertools import *
import math
import random


def P(params, xs):
  assert len(params) == len(xs)
  logit = sum(c * x for c, x in izip(params, xs))
  prob = 1 / (1 + math.exp(-logit))
  return min(max(prob, 1e-4), 1 - 1e-4)


def PDeriv(params, xs, sign):
  assert len(params) == len(xs)
  logit = sum(c * x for c, x in izip(params, xs))
  return 1 / (1 + math.exp(sign * logit))


def AddConstantsToData(data):
  if not data:
    return []
  element_type = type(data[0])
  new_data = []
  for xs in data:
    new_data.append(xs + element_type((1,)))
  return new_data


def GenerateRandomVariables(true_params, xs):
  return [int(random.random() <= P(true_params, x)) for x in xs]


def LikelihoodOfData(params, xs_list, y_list, priors=()):
  sum_log_likelihood = 0.0
  for xs, y in izip(xs_list, y_list):
    p = P(params, xs)
    if y == 0:
      p = 1 - p
    sum_log_likelihood += math.log(p)
  # We assume priors is a list of (mu, sigma) pairs representing a gaussian
  # distribution on the parameter values.  If there are no priors this will be
  # a no-op.
  for p, (mu, sigma) in izip(params, priors):
    sum_log_likelihood -= (p - mu) * (p - mu) / sigma   # - 0.5 Log(2 * pi * sigma), a constant we can ignore here
  return sum_log_likelihood


def LikelihoodDerivative(params, xs_list, y_list, priors=()):
  derivatives = [0.0] * len(params)
  for xs, y in izip(xs_list, y_list):
    p = P(params, xs)
    sign = (y == 1 and 1 or -1)
    p_deriv = PDeriv(params, xs, sign)
    for n, x in enumerate(xs):
      derivatives[n] += sign * x * p_deriv
  # We assume priors is a list of (mu, sigma) pairs representing a gaussian
  # distribution on the parameter values.  If there are no priors this will be
  # a no-op.
  for n, (p, (mu, sigma)) in enumerate(izip(params, priors)):
    derivatives[n] -= 2 * (p - mu) / sigma
  return derivatives


def LogisticRegressionParameters(xs_list, y_list, priors=(), max_steps=1000,
                                 max_stepsize_resets_per_iteration=5,
                                 stepsize_reset_factor=0.33,
                                 stepsize_increase_factor=1.05,
                                 minimum_derivative_size=1e-4,
                                 minimum_likelihood_increase=1e-5,
                                 debug_output=False,
                                 use_quadratic_stepsize_optimization=False,
                                 min_quadratic_benefit=0.1,
                                 turn_quadratic_stepsize_optimization_off=False):
  if not xs_list or not y_list:
    return []
  import time
  start_time = time.time()
  num_params = len(xs_list[0])
  params = [random.gauss(0, 2) for n in range(num_params)]
  step_size = 1.0 / len(xs_list)
  likelihood = LikelihoodOfData(params, xs_list, y_list, priors)

  for iteration in xrange(max_steps):
    derivatives = LikelihoodDerivative(params, xs_list, y_list, priors)
    magnitude_of_derivative = sum(d * d for d in derivatives)
    if debug_output:
      print "Step %4d, Likelihood = %10.3f, step_size = %4e, |dL| = %4e" % (iteration,
                                                                            likelihood,
                                                                            step_size,
                                                                            magnitude_of_derivative)
    if magnitude_of_derivative < minimum_derivative_size * minimum_derivative_size:
      if debug_output:
        print "derivative beneath minimum, terminating"
      break

    if use_quadratic_stepsize_optimization:
      new_params = [x + step_size * d for x, d in izip(params, derivatives)]
      simple_stepsize_likelihood = new_likelihood = LikelihoodOfData(new_params, xs_list, y_list, priors)
      delta = new_likelihood - likelihood
      tmp = magnitude_of_derivative * step_size
      quadratic_stepsize_correction = 0.5 * tmp / (tmp - delta)
      # Note: sometimes this number oscillates.  I imagine that's a good
      # sign to stop the quadratic optimization...
      step_size *= quadratic_stepsize_correction
    for reset in range(max_stepsize_resets_per_iteration):
      new_params = [x + step_size * d for x, d in izip(params, derivatives)]
      new_likelihood = LikelihoodOfData(new_params, xs_list, y_list, priors)
      if (turn_quadratic_stepsize_optimization_off and
          use_quadratic_stepsize_optimization and
          new_likelihood - simple_stepsize_likelihood < min_quadratic_benefit):
        use_quadratic_stepsize_optimization = False
      if False and debug_output:
        print "got new likelihood", new_likelihood
      if new_likelihood > likelihood:
        break
      step_size *= stepsize_reset_factor
    else:
      raise Exception, "step size issue!"
    if new_likelihood - likelihood < minimum_likelihood_increase:
      if debug_output:
        print "likelihood increase below minimum, terminating..."
      break
    if not use_quadratic_stepsize_optimization:
      step_size *= stepsize_increase_factor
    step_size *= stepsize_increase_factor
    likelihood = new_likelihood
    params = new_params
  else:
    raise Exception, "max iterations obtained!"

  if debug_output:
    print "took", time.time() - start_time, "seconds"
  return params


def main():
  import sys
  seed = random.randint(0, 100000)
  random.seed(seed)
  print "SEED", seed

  failures = []
  for n in range(100):
    print >> sys.stderr, n
    xs = [tuple(int(random.random() < 0.5) for n in range(1))
          for datapoint in range(1000)]
    xs_list = AddConstantsToData(xs)
    params = [random.gauss(0, 2) for m in range(2)]
    priors = [(0, 2), (0, 2)]
    ys = GenerateRandomVariables(params, xs_list)
    try:
      estimated_params = LogisticRegressionParameters(xs_list, ys, priors=(), debug_output=True)
      estimated_params2 = LogisticRegressionParameters(xs_list, ys, priors=priors, debug_output=True)
      error = math.sqrt(sum(e * e for e in (g - r for g, r in izip(estimated_params, params))))
      print " ".join(imap(str, [g - r for g, r in izip(estimated_params, params)])), estimated_params
      error = math.sqrt(sum(e * e for e in (g - r for g, r in izip(estimated_params2, params))))
      print " ".join(imap(str, [g - r for g, r in izip(estimated_params2, params)])), estimated_params2
    except Exception, e:
      raise
      failures.append(e)
    break

  print "real params", params
  import collections
  reasons = collections.defaultdict(int)
  for exception in failures:
    reasons[str(exception)] += 1
  print >> sys.stderr, "%d failures / %d total, %s" % (len(failures), n, reasons)

  return

  xs = [() for n in range(100)]
  xs_list = AddConstantsToData(xs)

  params = [1.0]
  ys = GenerateRandomVariables(params, xs_list)
  estimated_params = LogisticRegressionParameters(xs_list, ys)
  print estimated_params
  return

  tmp = []
  for n in range(100):
    random_params = [random.gauss(0, 2) for n in range(len(params))]
    likelihood = LikelihoodOfData(random_params, xs, ys)
    derivatives = LikelihoodDerivative(random_params, xs, ys)
    tmp.append((random_params[0], likelihood, derivatives[0]))

  tmp.sort()

  for n, (alpha, likelihood, deriv) in enumerate(tmp):
    if n == 0:
      # print "%+5.3f %+8.3f %+8.3f" % (alpha, likelihood, deriv)
      pass
    else:
      prev_alpha, prev_likelihood, _ = tmp[n - 1]
      estimated_deriv = (likelihood - prev_likelihood) / (alpha - prev_alpha)
      print "%+5.3f %8.3f %+8.3f %+8.3f" % (alpha, likelihood, deriv, estimated_deriv)


if __name__ == '__main__':
  main()
