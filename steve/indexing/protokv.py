"""A very simple file format for reading and writing lists of
key value pairs whose values are protocol buffers.
"""

from cobra.steve.indexing import protolist
from cobra.steve.indexing.proto import kv_pb2


class ProtoKeyValueFile(object):
    def __init__(self, prototype, path, mode):
        self.plf = protolist.ProtoListFile(kv_pb2.KeyValuePair, path, mode)
        self.prototype = prototype

    def Close(self):
        self.plf.Close()

    def Output(self, key, value):
        kv_proto = kv_pb2.KeyValuePair()
        kv_proto.key = key
        kv_proto.value = value.SerializeToString()
        self.plf.Output(kv)

    def MakeNewProto(self):
        return self.prototype()

    def __iter__(self):
        for kv_proto in self.plf:
            value = self.MakeNewProto()
            value.ParseFromString(kv_proto.value)
            yield kv_proto.key, value

