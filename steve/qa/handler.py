"""The object that actually handles generating new questions for a user
as well as accepting responses.
"""

import struct

from cobra.steve.qa import investigator


class QuestionHandler(object):
  def __init__(self, datastore):
    self.datastore = datastore
    self.investigator = investigator.QuestionInvestigator()

  def GetNewQuestion(self, user_id):
    history = self.datastore.GetOrCreateUserHistory(user_id)
    new_question = history.questions.add()
    self.investigator.FillNextQuestion(history, new_question)
    self.datastore.SetUserHistory(user_id, history)
    new_question.id = EncodeUserIdAndIndex(user_id, len(history.question))
    return new_question

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
  return struct.unpack("%H%H", struct.pack("%I", question_id))
  

def EncodeUserIdAndIndex(user_id, n):
  """The inverse of ExtractUserIdAndIndex."""
	return struct.unpack("%I", struct.pack("%H%H", user_id, n))
  
  

def FillEventProto(event_proto, event):
  raise NotImplementedError
