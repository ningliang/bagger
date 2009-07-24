"""A class to decide, given a user's question history, what the
next question to show them should be.
"""

import os.path
import csv
import random

from cobra.steve.util.prelude import *
from cobra.steve.util import cobrastuff

flags.DefineString("questions_file_path", "steve/qa/questions.csv",
                   "The path to the quesitons file, relative to cobra.")



class QuestionInvestigator(object):
  def __init__(self, questions_file_path=None):
    if questions_file_path is None:
      questions_file_path = FLAGS.questions_file_path
    self.questions_file_path = os.path.join(cobrastuff.CobraDir(),
                                            questions_file_path)
    self.questions = LoadQuestionsFromFile(questions_file_path)

  def FillNextQuestion(self, user_history, question_pb):
    # For now we just generate a random question.
    question = random.choice(self.questions.values())
    question.FillQuestionInstance(user_history, question_pb)

  def RenderQuestionProtoForXMLRPC(self, question_pb):
    pass


def LoadQuestionsFromFile(question_file_path):
  reader = csv.reader(open(question_file_path))
  responses = {}
  questions = {}
  for row in reader:
    row = map(str.strip, row)
    if len(row) <= 1:
      continue
    if row[0].upper() == 'RESPONSE':
      response_id, response_type = row[1], row[2]
      choices = row[3:]
      responses[response_type] = ResponseSet(response_id, response_type, choices)
    elif row[0].upper() == 'QUESTION':
      question_id, response_type, text = row[1], row[2], row[3]
      choices = row[4:]
      questions[question_id] = Question(question_id, text, responses[response_type])
    else:
      pass
  return questions



class Question(object):
  def __init__(self, question_id, text, response_set):
    self.question_id = question_id
    self.text = text
    self.response_set = response_set

  def FillQuestionInstance(self, user_history, question_pb):
    question_pb.type = self.question_id
    question_pb.question_text = self.text
    for choice in self.response_set.GenerateChoicesInstance(user_history):
      question_pb.choices.add(choice)


def ResponseSet(response_id, response_type, choices):
  if response_id > 0:
    return MultipleChoiceResponseSet(choices)
  elif response_type == 'OneBlankEntry':
    return MultipleBlanksResponseSet(1)
  elif response_type == 'ThreeBlankEntries':
    return MultipleBlanksResponseSet(3)
  elif response_type == 'FiveBlankEntries':
    return MultipleBlanksResponseSet(5)


class MultipleChoiceResponseSet(object):
  def __init__(self, choices):
    self.choices = choices

  def GenerateChoicesInstance(self, user_history):
    """Given a user's previous question answer history, generate a response selection.
    For most response types, this will just return the choices."""
    return self.choices[:]

  def UserInterfaceQuestionType(self):
    """Return a 'question type' appropriate for this result set.  For instance, should
    return 'ProductQuestion' for multiple handbags, etc.  This response is based on the
    given response_type.
    """
    return "MultipleChoice"


class MultipleBlanksResponseSet(object):
  def __init__(self, number_of_blanks):
    self.number_of_blanks = number_of_blanks

  def GenerateChoicesInstance(self, user_history):
    

  def UserInterfaceQuestionType(self):
    return "%dBlanks" % self.number_of_blanks
