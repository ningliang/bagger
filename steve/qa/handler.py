"""The object that actually handles generating new questions for a user
as well as accepting responses.
"""

from cobra.steve.qa import investigator


class QuestionHandler(object):
  def __init__(self, datastore):
    self.datastore = datastore
    self.investigator = investigator.QuestionInvestigator()

  def GetNewQuestion(self, user_id):
    history = self.datastore.GetUserHistory(user_id)
    new_question = history.questions.add()
    self.investigator.FillNextQuestion(history, new_question)
    new_question.id = MakeQuestionId(user_id, len(history.questions))
    self.datastore.SetUserHistory(user_id, history)
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



def FillEventProto(event_proto, event):
  pass
