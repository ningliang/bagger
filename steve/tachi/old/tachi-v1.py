import random
import math


class FloatingPoint(object):
  Zero = 0.0
  Plus = staticmethod(lambda x, y: x + y)
  Times = staticmethod(lambda x, y: x * y)


class BinaryPoint(object):
  Zero = False
  Plus = staticmethod(lambda x, y: x or y)
  Times = staticmethod(lambda x, y: x and y)

# TODO(fedele): add more vector (ring) methods here.


def CircularImpl(cs, xs, IndexingScheme, Strategy):
  assert len(cs) == len(xs)
  N = len(cs)
  ts = N * [Strategy.Zero]
  for k, c in enumerate(cs):
    for j, t in enumerate(ts):
      ts[j] = Strategy.Plus(t, Strategy.Times(c, xs[IndexingScheme(j, k) % N]))
  return ts


# TODO(fedele): automatically infer the strategy from the vector that gets
# passed in.
def CircularConvolution(cs, xs, strategy=FloatingPoint):
  return Normalize(CircularImpl(cs, xs, lambda j, k: j - k, strategy))


def CircularCorrelation(cs, xs, strategy=FloatingPoint):
  return Normalize(CircularImpl(cs, xs, lambda j, k: j + k, strategy))


def TraceComposition(xs, ys, strategy=FloatingPoint):
  return [strategy.Plus(x, y) for x, y in zip(xs, ys)]


def Normalize(xs):
  norm = math.sqrt(Dot(xs, xs))
  # norm = sum(abs(x) for x in xs)
  return [x / norm for x in xs]


def Dot(xs, ys):
  return sum(x * y for x, y in zip(xs, ys))


def RandomVector(n):
  """Return a random n-vector whose components are independently
  drawn from N(0, 1/n)"""
  return [random.gauss(0.0, 1.0 / n) for i in xrange(n)]



def main():
  N = 1000
  As = RandomVector(N)
  bs = RandomVector(N)
  cs = RandomVector(N)
  ds = RandomVector(N)
  es = RandomVector(N)
  fs = RandomVector(N)
  ys = RandomVector(N)
  T2 = TraceComposition(CircularConvolution(As, bs),
                        TraceComposition(CircularConvolution(cs, ds),
                                         CircularConvolution(es, fs)))
  for cue_name, cue in (("As", As), ("cs", cs), ("es", es), ("ys", ys)):
    response = CircularCorrelation(cue, T2)
    coeffs = map(lambda x: Dot(response, x), (bs, ds, fs))
    print "Cue %s" % cue_name
    for name, coeff in zip(("bs", "ds", "fs"), coeffs):
      print "  %s = %f" % (name, coeff)
    print

  return
  cs = RandomVector(N)
  xs = RandomVector(N)
  ts = CircularConvolution(cs, xs)
  noisy_xs = CircularCorrelation(cs, ts)

  # print "cs = ", cs
  # print "xs = ", xs
  print "Dot(cs, xs) = ", Dot(cs, xs)
  print "-" * 40
  # print ts
  print "Dot(ts, cs) = ", Dot(ts, cs)
  print "Dot(ts, xs) = ", Dot(ts, xs)
  print "-" * 40
  # print noisy_xs
  print "Dot(ns, cs) = ", Dot(noisy_xs, cs)
  print "Dot(ns, xs) = ", Dot(noisy_xs, xs)
  print "-" * 40
  pass


if __name__ == '__main__':
  main()
