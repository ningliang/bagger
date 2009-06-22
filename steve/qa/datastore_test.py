from cobra.steve.app import test
from cobra.steve.qa.datastore import *
from cobra.steve.qa.proto import qa_pb2


class BasicDataStoreTest(object):
  ds = None

  def MakeFakeHistories(self, question_sizes):
    def MakeFakeHistory(user_id, size):
      history = qa_pb2.UserHistory()
      history.user_id = user_id
      for n in range(size):
        question = history.questions.add()
      return history
    histories = [MakeFakeHistory(n, size) for n, size in enumerate(question_sizes)]
    for history in histories:
      self.ds.SetUserHistory(history.user_id, history)

  def testBasicFunctionality(self):
    self.MakeFakeHistories(question_sizes=(1,2,3))
    self.assertEqual(2, len(self.ds.GetUserHistory(1).questions))
    self.assertEqual(3, len(self.ds.GetUserHistory(2).questions))
    history = self.ds.GetUserHistory(0)
    history.questions.add()
    self.ds.SetUserHistory(0, history)
    self.assertEqual(3, len(self.ds.GetUserHistory(2).questions))
    self.assertEqual(2, len(self.ds.GetUserHistory(0).questions))
    self.assertEqual(0, len(self.ds.GetOrCreateUserHistory(4).questions))
    self.assertEqual(3, len(self.ds.GetOrCreateUserHistory(2).questions))

  def testRaisesKeyErrors(self):
    self.assertRaises(KeyError, self.ds.GetUserHistory, 0)
    self.MakeFakeHistories(question_sizes=(1,2,3))
    history = self.ds.GetUserHistory(0)
    self.assertRaises(KeyError, self.ds.GetUserHistory, 4)


class TestInMemoryDataStore(BasicDataStoreTest, test.TestCase):
  def setUp(self):
    self.ds = InMemoryDataStore()


class TestLocalDataStore(BasicDataStoreTest, test.TestCase):
  def setUp(self):
    self.ds = LocalDataStore(location=":memory:")


if __name__ == '__main__':
  import unittest
  # unittest.main()
  test.run()
