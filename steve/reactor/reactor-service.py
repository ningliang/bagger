from twisted.application import service, internet
from twisted.internet import reactor, defer

from cobra.steve.util.prelude import *
from cobra.steve.rpc import pbrpc
from cobra.steve.reactor.proto import reactor_pb2

flags.DefineString('host', '127.0.0.1', "The server's ip address")
flags.DefineInteger('port', '1337', "The port to connect to")


class ReactorServiceHandler(reactor_pb2.ReactorService):
  def __init__(self, impl, *args, **kwargs):
    super(ReactorServiceHandler, self).__init__(*args, **kwargs)
    self.impl = impl

  def GetTaskInfo(self, controller, request, callback):
    response = reactor_pb2.TaskInfoResponse()
    d = defer.maybeDeferred(self.impl.GetTaskInfo, request, response)
    d.addCallback(callback)
    


class ReactorServiceImpl(object):
  def __init__(self):
    pass
    
  def GetTaskInfo(self, request, response):
    print request
    for name in ("Foobar", "SpamMethod"):
      response.info.add().name = name      
    print response
    return response
    
  

def main(argv):
  impl = ReactorServiceImpl()
  test_service = ReactorServiceHandler(impl)
  test_service.factory = factory = pbrpc.Factory(test_service)
  reactor.listenTCP(FLAGS.port, factory)
  print "Starting reactor-server on port %d" % FLAGS.port
  reactor.run()


if __name__ == '__main__':
  app.run()
    