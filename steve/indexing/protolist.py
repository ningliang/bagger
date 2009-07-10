"""A very simple file format for reading and writing lists of
protocol buffers.
"""

import struct

from cobra.steve.util.prelude import *


class ProtoListFile(object):
    def __init__(self, prototype, path, mode):
        if 'b' not in mode:
            mode += 'b'
        self.f = open(path, mode)
        self.prototype = prototype

    def Close(self):
        self.f.close()

    def Output(self, value):
        serialized = value.SerializeToString()
        MAX_LEN = 2 ** 16
        assert len(serialized) < MAX_LEN
        self.f.write(struct.pack("H", len(serialized)))
        self.f.write(serialized)
        self.f.flush()

    def MakeNewProto(self):
        return self.prototype()

    def __iter__(self):
        self.f.seek(0)
        while True:
            size_buffer = self.f.read(2)
            if not size_buffer:
                break
            size = struct.unpack("H", size_buffer)[0]
            proto = self.MakeNewProto()
            serialized = self.f.read(size)
            proto.ParseFromString(serialized)
            yield proto


def main(argv):
    from cobra.steve.indexing import test_pb2
    import random
    plf = ProtoListFile(test_pb2.MyTestProto, '/tmp/testprotofile', 'w')
    for n in range(5):
        p = test_pb2.MyTestProto()
        p.name = "John Doe %d" % n
        if random.random() < 0.5:
            p.age = random.randint(5, 35)
        if random.random() < 0.25:
            p.birthday = "July 9th, 1985"
        plf.Output(p)
    plf.Close()

    plf = ProtoListFile(test_pb2.MyTestProto, '/tmp/testprotofile', 'r')
    for p in plf:
        print "[%-25s][%-25s][%-25s]" % (p.name, p.age, p.birthday)


if __name__ == '__main__':
    app.run()

            
            

    
