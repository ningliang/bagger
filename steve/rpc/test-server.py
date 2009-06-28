from twisted.application import service, internet
from twisted.internet import reactor

from cobra.steve.util.prelude import *
from cobra.steve.rpc import pbrpc
from cobra.steve.rpc.proto import test_pb2

flags.DefineString('host', '127.0.0.1', "The server's ip address")
flags.DefineInteger('port', '1337', "The port to connect to")


class TestServiceHandler(test_pb2.TestService):
  def Foobar(self, controller, testRequest, callback):
    response = test_pb2.TestResponse()
    if random.random() < 0.5:
      response.z = "you got lucky"
    response.alpha = "alpha %s" % testRequest.x
    print "Foobar", testRequest
    reactor.callLater(random.randint(1, 5), callback, response)

  def SpamMethod(self, controller, testRequest, callback):
    response = test_pb2.TestResponse()
    response.alpha = "spam"
    print "SpamMethod", testRequest
    callback(response)



def main(argv):
  test_service = TestServiceHandler()
  test_service.factory = factory = pbrpc.Factory(test_service)
  reactor.listenTCP(FLAGS.port, factory)
  print "Starting test-server on port %d" % FLAGS.port
  reactor.run()


if __name__ == '__main__':
  app.run()
