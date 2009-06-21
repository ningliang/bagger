"""Defines the interface to store and retrieve data persistantly, as
well as includes several interface implementations:

  - LocalDataStore    - a local data store that uses the harddrive to store info.
  - RemoteDataStore   - a data store that is hosted "remotely" in some sense.
  - InMemoryDataStore - a data store that is done completely in memory.

See the code and comments for more information.
"""

from cobra.steve.qa.proto import qa_pb


class DataStoreInterface(object):
  def GetUserHistory(self, user_id):
    raise NotImplementedError

  def SetUserHistory(self, user_id, history):
    raise NotImplementedError


class InMemoryDataStore(DataStoreInterface):
  def __init__(self):
    self.questions = {}
    self.histories = {}
    self.cur_question_id = 0

  def GetUserHistory(self, user_id):
    try:
      return self.histories[user_id]
    except KeyError:
      return self.histories.setdefault(user_id, qa_pb.UserHistory())

  def SetUserHistory(self, user_id, history):
    self.histories[user_id] = history


class LocalDataStore(DataStoreInterface):
  pass


class RemoteDataStore(DataStoreInterface):
  pass
