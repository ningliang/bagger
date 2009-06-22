import unittest
from cobra.steve.qa.handler import *

from cobra.steve.qa import datastore
from cobra.steve.qa.proto import qa_pb2



class TestHandler(unittest.TestCase):
  def setUp(self):
    self.datastore = datastore.InMemoryDataStore()

  def MakeHandler(self):
    return QuestionHandler(self.datastore)
  
  def testBasicFunctionality(self):
    handler = self.MakeHandler()
    id1 = handler.GetNewQuestion(0).id
    id2 = handler.GetNewQuestion(0).id
    id3 = handler.GetNewQuestion(1).id    
    handler.SetQuestionResponse(id1, 0)
    handler.SetQuestionResponse(id3, 1)
    handler.SetQuestionResponse(id1, 2)
    history = self.datastore.GetUserHistory(0)
    self.assertEqual(2, history.questions[0].response)
    self.assertFalse(history.questions[1].HasField('response'))    
    history = self.datastore.GetUserHistory(1)
    self.assertEqual(1, history.questions[0].response) 


    
class TestEncoding(unittest.TestCase):
  def testEncoding(self):      
    self.assertEqual(0, EncodeUserIdAndIndex(0, 0))
    import random
    for n in range(10):
      original = tuple(random.randint(0, 100) for n in range(2))
      self.assertEqual(original, ExtractUserIdAndIndex(EncodeUserIdAndIndex(*original)))

      

if __name__ == '__main__':
  unittest.main()

