from cobra.steve.util.prelude import *

from twisted.internet import reactor

from txjsonrpc.web.jsonrpc import Proxy


flags.DefineInteger('port', 1337, 'The port to run the service on.')


def PrintValue(value):
  print "Result: %s" % str(value)
  reactor.stop()

def PrintError(error):
  print "Error:", error
  reactor.stop()


def main(argv):
  print "Making remote call..."
  proxy = Proxy('http://127.0.0.1:%d/RPC2/' % FLAGS.port)
  proxy.callRemote('NingsAwesomeMethod', 3, 8).addCallbacks(PrintValue, PrintError)
  # proxy.callRemote('GetNewQuestion', 0).addCallbacks(PrintValue, PrintError)
  print "OK..."
  reactor.run()


if __name__ == '__main__':
  app.run()
