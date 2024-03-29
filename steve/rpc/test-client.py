from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.internet.defer import Deferred, DeferredList


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

  
def ChainRequest(response, proxy):
  request = test_pb2.TestRequest()
  request.x = len(response.alpha) + 10 * (response.z != '')
  return proxy.SpamMethod(request)
  

def MakeRequests(proxy):
  ds = []
  for n in range(10):
    request = test_pb2.TestRequest()
    request.x = n
    request.y = "foobar %d" % n
    d = proxy.Foobar(request)
    d.addCallback(ChainRequest, proxy)
    ds.append(d)
  print "DONE MAKING REQUESTS"
  return DeferredList(ds)

  
def PrintResult(results):
  for n, (success, result) in enumerate(results):
    print n, success, result


def main(argv):
  d = ClientCreator(reactor, pbrpc.Protocol).connectTCP(FLAGS.host, FLAGS.port)
  d.addCallbacks(MakeProxy, ErrorMakingProxy)
  d.addCallbacks(MakeRequests)
  d.addCallbacks(PrintResult)
  d.addCallbacks(lambda x: reactor.stop())
  reactor.run()
  return


if __name__ == '__main__':
  app.run()
