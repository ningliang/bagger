from cobra.steve.util.prelude import *
from cobra.steve.experimental.gcluster.proto import worddata_pb2
from cobra.steve.indexing import protolist

import multiprocessing


def StdoutWorker(stdout_queue):
  while True:
    msg = stdout_queue.get()
    print >> sys.stdout, msg


def StartStdoutWorkerWithQueue():
  stdout_queue = multiprocessing.Queue()
  stdout_process = multiprocessing.Process(target=StdoutWorker, args=(stdout_queue,))
  stdout_process.daemon = True
  stdout_process.start()
  return stdout_queue, stdout_process


def WorddataFileOutputWorker(worddata_queue, output_path, append_to_existing_files=False):
  mode = append_to_existing_files and 'a' or 'w'
  output_list = protolist.ProtoListFile(worddata_pb2.WordData, output_path, mode)
  try:
    while True:
      worddata_serialized = worddata_queue.get()
      if worddata_serialized is None:
        break
      output_list.OutputRaw(worddata_serialized)
  finally:
    output_list.Close()


def StartWorddataFileOutputWorkerWithQueue(output_path, append_to_existing_files=False):
  queue = multiprocessing.Queue()
  process = multiprocessing.Process(target=WorddataFileOutputWorker,
                                    args=(queue, output_path, append_to_existing_files))
  process.daemon = True
  process.start()
  return queue, process
