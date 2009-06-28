from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.internet.defer import Deferred, DeferredList


from cobra.steve.util.prelude import *
from cobra.steve.rpc import pbrpc
from cobra.steve.reactor.proto import reactor_pb2

flags.DefineString('host', '127.0.0.1', "The server's ip address")
flags.DefineInteger('port', '1337', "The port to connect to")


def PrintValue(value):
  print "Result:"
  print value


def PrintError(error):
  print "Error:", error


def MakeProxy(protocol):
  return pbrpc.Proxy(reactor_pb2.ReactorService_Stub(protocol))


def ErrorMakingProxy(error):
  print "Error making proxy:", error

  
  

def MakeRequests(proxy):  
  request = reactor_pb2.TaskInfoRequest()
  request.command = request.LIST_ALL_TASKS
  return proxy.GetTaskInfo(request)


def main(argv):
  print "hi"
  d = ClientCreator(reactor, pbrpc.Protocol).connectTCP(FLAGS.host, FLAGS.port)
  d.addCallbacks(MakeProxy, ErrorMakingProxy)
  d.addCallbacks(MakeRequests)  
  d.addCallbacks(PrintValue, PrintError)
  d.addCallbacks(lambda x: reactor.stop())  
  reactor.run()
  return


if __name__ == '__main__':
  app.run()
