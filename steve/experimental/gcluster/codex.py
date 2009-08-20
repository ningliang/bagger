"""File for printing general 

"""

from cobra.steve.util.prelude import *
from cobra.steve.indexing import protolist
from cobra.steve.experimental.gcluster.proto import worddata_pb2

flags.DefineString("kvf", None, "Path to the key-value file to output")

# TODO(fedele): make this program work for arbitrary value protos
# flags.DefineString("value_proto", None, "The python module path for the proto class")


def main(argv):
  plf = protolist.ProtoListFile(worddata_pb2.WordData, FLAGS.kvf, 'r')
  n = 0
  for n, worddata in enumerate(plf):
    print worddata
    print



if __name__ == '__main__':
  app.run()
