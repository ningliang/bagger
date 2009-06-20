"""The actual QA server.

Exposes the QuestionAnswer service via JSON-RPC on /RPC2/
Exports the following methods:

  - GetNewQuestion(user_id)
  - SetQuestionResponse(question_id, choice)
  - AddQuestionEvents(question_id, events)

See the comments on the corresponding methods in QuestionHandlerResource
for more details.
"""

from cobra.steve.util.prelude import *
from cobra.steve.qa import handler, datastore

from twisted.web import server, resource
from twisted.internet import reactor, defer

from txjsonrpc.web import jsonrpc


flags.DefineInteger('port', 1337, 'The port to run the service on.')


class QuestionHandlerResource(jsonrpc.JSONRPC):
  """The Twisted Resource that acts as a wrapper around the basic
  QuestionHandler object that we're going to publish."""
  addSlash = True
  isLeaf = True

  def __init__(self, question_handler, *args, **kwargs):
    jsonrpc.JSONRPC.__init__(self, *args, **kwargs)
    self.question_handler = question_handler

  def jsonrpc_GetNewQuestion(self, user_id):
    """Requests that a new question be generated for the given user.
    Returns a QuestionInstance.

      @user_id - the user_id of the user we're generating a question for.
    """
    return self.question_handler.GetNewQuestion(user_id)

  def jsonrpc_SetQuestionResponse(self, question_id, choice):
    """Notify the service about a response the user made.  Return True
    on success, False otherwise.

      @question_id - the question instance id of the question answered.
      @choice      - the choice the user made as an index.
    """
    return self.question_handler.SetQuestionResponse(question_id, choice)

  def jsonrpc_AddQuestionEvents(self, question_id, events):
    """Notify the service about events that fired when answering a
    Question.  Returns True on success, False otherwise.

      @question_id - the question instance id of the question.
      @events      - a list of (eventtype, time) pairs.
    """
    return self.question_handler.AddQuestionEvents(question_id, events)


def main(argv):
  root = resource.Resource()
  my_data_store = datastore.LocalDataStore()
  question_handler = handler.QuestionHandler(my_data_store)
  root.putChild('RPC2', QuestionHandlerResource(question_handler))
  site = server.Site(root)
  reactor.listenTCP(FLAGS.port, site)
  print "starting QA server on port %d" % FLAGS.port
  reactor.run()


if __name__ == '__main__':
  app.run()
