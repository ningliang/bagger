from cobra.steve.util.prelude import *

from twisted.internet import reactor
from twisted.web.xmlrpc import Proxy


flags.DefineString('host', '127.0.0.1', 'The servers ip')
flags.DefineInteger('port', 1337, 'The port to run the service on.')


def PrintValue(value):
  print "Result: %s" % str(value)
  reactor.stop()


def PrintError(error):
  print "Error:", error
  reactor.stop()


def main(argv):
  print "Making remote call..."
  proxy = Proxy('http://%s:%d/RPC2/' % (FLAGS.host, FLAGS.port))
  proxy.callRemote('GetNewQuestion', 0).addCallbacks(PrintValue, PrintError)
  print "OK..."
  reactor.run()


if __name__ == '__main__':
  app.run()
