"""The object that actually handles the Question RPCs from the
qa-service.
"""

import struct

from cobra.steve.qa.investigator import QuestionInvestigator


class QuestionHandler(object):
  def __init__(self, datastore, investigator=None):
    self.datastore = datastore
    if investigator is None:
      investigator = QuestionInvestigator()
    self.investigator = investigator

  def GetNewQuestion(self, user_id):
    history = self.datastore.GetOrCreateUserHistory(user_id)
    new_question_id = EncodeUserIdAndIndex(user_id, len(history.questions))
    new_question = history.questions.add()
    self.investigator.FillNextQuestion(history, new_question)
    self.datastore.SetUserHistory(user_id, history)
    new_question.id = new_question_id
    return self.investigator.RenderQuestionProtoToXML(new_question)

  def SetQuestionResponse(self, question_id, response):
    user_id, index = ExtractUserIdAndIndex(question_id)
    history = self.datastore.GetUserHistory(user_id)
    history.questions[index].response = response
    self.datastore.SetUserHistory(user_id, history)
    return True

  def AddQuestionEvents(self, question_id, events):
    user_id, index = ExtractUserIdAndIndex(question_id)
    history = self.datastore.GetUserHistory(user_id)
    question = history.questions[index]
    for event in events:
      FillEventProto(question.events.add(), event)
    self.datastore.SetUserHistory(user_id, history)
    return True


def ExtractUserIdAndIndex(question_id):
  """The question_id is actually encoded as follows:
    upper 16 bits: user_id
    lower 16 bits: question index
  Note that if we ever need to change this, well, good...
  """
  return struct.unpack("HH", struct.pack("I", question_id))


def EncodeUserIdAndIndex(user_id, n):
  """The inverse of ExtractUserIdAndIndex."""
  return struct.unpack("I", struct.pack("HH", user_id, n))[0]


def FillEventProto(event_proto, event):
  raise NotImplementedError
