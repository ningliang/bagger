"""Defines the interface to store and retrieve data persistantly, as
well as includes several interface implementations:

  - LocalDataStore    - a local data store that uses the harddrive to store info.
  - RemoteDataStore   - a data store that is hosted "remotely" in some sense.
  - InMemoryDataStore - a data store that is done completely in memory.

See the code and comments for more information.
"""


class DataStoreInterface(object):
  def __init__(self):
    pass


class MockDataStore(DataStoreInterface):
  pass


class LocalDataStore(DataStoreInterface):
  pass


class RemoteDataStore(DataStoreInterface):
  pass


class InMemoryDataStore(DataStoreInterface):
  pass
