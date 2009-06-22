"""Defines the interface to store and retrieve data persistantly, as
well as includes several interface implementations:

  - LocalDataStore    - a local data store that uses the harddrive to store info.
  - RemoteDataStore   - a data store that is hosted "remotely" in some sense.
  - InMemoryDataStore - a data store that is done completely in memory.

See the code and comments for more information.
"""

import sqlite3

from cobra.steve.qa.proto import qa_pb2


class DataStoreInterface(object):
  def GetUserHistory(self, user_id):
    raise NotImplementedError

  def SetUserHistory(self, user_id, history):
    raise NotImplementedError
    
  def GetOrCreateUserHistory(self, user_id):
    try:
      return self.GetUserHistory(user_id)
    except KeyError:
      history = qa_pb2.UserHistory()
      history.user_id = user_id
      self.SetUserHistory(user_id, history)
      return history


class InMemoryDataStore(DataStoreInterface):
  def __init__(self):
    self.histories = {}    

  def GetUserHistory(self, user_id):
    return self.histories[user_id]
    
  def SetUserHistory(self, user_id, history):
    self.histories[user_id] = history


class LocalDataStore(DataStoreInterface):
  def __init__(self, location=":memory:"):
    self.connection = sqlite3.connect(location)
    c = self.connection.cursor()
    c.execute("""create table if not exists userhistories (userid, historyproto blob, primary key (userid))""")
    self.connection.commit()
    
  def GetUserHistory(self, user_id):
    c = self.connection.cursor()
    c.execute("select * from userhistories where userid=?", (user_id,))    
    try:      
      _, proto_bytes = c.fetchone()
    except TypeError:
      raise KeyError(user_id)
    user_history = qa_pb2.UserHistory()    
    user_history.ParseFromString(proto_bytes)
    return user_history
    
  def SetUserHistory(self, user_id, history):
    c = self.connection.cursor()
    toinsert = (buffer(history.SerializeToString()), user_id)    
    c.execute("update userhistories set historyproto=? where userid=?", toinsert)
    if c.rowcount == 0:
      c.execute("insert into userhistories (historyproto, userid) values (?, ?)", toinsert)
    self.connection.commit()
    
      
    
      
    


class RemoteDataStore(DataStoreInterface):
  pass
