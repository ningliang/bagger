from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator

from cobra.steve.util.prelude import *
from cobra.steve.rpc import pbrpc
from cobra.steve.rpc.proto import test_pb2

flags.DefineString('host', '127.0.0.1', "The server's ip address")
flags.DefineInteger('port', '1337', "The port to connect to")


def PrintValue(value):
  print "Result:"
  print value


def PrintError(error):
  print "Error:", error


def MakeProxy(protocol):
  return pbrpc.Proxy(test_pb2.TestService_Stub(protocol))


def ErrorMakingProxy(error):
  print "Error making proxy:", error


def MakeRequests(proxy):
  for n in range(10):
    request = test_pb2.TestRequest()
    request.x = n
    request.y = "foobar %d" % n
    proxy.Foobar(request).addCallbacks(PrintValue, PrintError)
    proxy.SpamMethod(request).addCallbacks(PrintValue, PrintError)
  print "DONE MAKING REQUESTS"


def main(argv):
  d = ClientCreator(reactor, pbrpc.Protocol).connectTCP(FLAGS.host, FLAGS.port)
  d.addCallbacks(MakeProxy, ErrorMakingProxy)
  d.addCallbacks(MakeRequests)
  reactor.run()
  return


if __name__ == '__main__':
  app.run()
