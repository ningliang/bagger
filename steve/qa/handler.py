"""The object that actually handles generating new questions for a user
as well as accepting responses.
"""


class QuestionHandler(object):
  def __init__(self, datastore):
    self.datastore = datastore

  def GetNewQuestion(self, user_id):
    # TODO(fedele): look up the user, and if they aren't there add them
    # TODO(fedele): get all previously asked questions for this user, and
    #               determine the appropriate next question to return.
    # TODO(fedele): create a new QuestionInstance object in our database
    return QuestionInstance(0, 0, ['foo', 'bar', 'baz'])

  def SetQuestionResponse(self, question_id, response):
    # TODO(fedele): find the question_id in our database
    # TODO(fedele): update it with the given response
    return True

  def AddQuestionEvents(self, question_id, events):
    # TODO(fedele): find the question_id in our database
    # TODO(fedele): update it with the given events
    return True


class QuestionInstance(object):
  def __init__(self, question_id, question_type, choices):
    self.question_id = question_id
    self.question_type = question_type
    self.choices = choices
