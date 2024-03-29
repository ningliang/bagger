"""File for printing general 

"""

from cobra.steve.util.prelude import *
from cobra.steve.indexing import protokv
from cobra.steve.indexing.proto import handbag_pb2

flags.DefineString("kvf", None, "Path to the key-value file to output")

# TODO(fedele): make this program work for arbitrary value protos
# flags.DefineString("value_proto", None, "The python module path for the proto class")


def main(argv):
  kvf = protokv.ProtoKeyValueFile(handbag_pb2.PurchasePoint, FLAGS.kvf, 'r')
  n = 0
  for n, (key, value) in enumerate(kvf):
    print n, key, value
  print "printed %d bags" % n
    


if __name__ == '__main__':
  app.run()
