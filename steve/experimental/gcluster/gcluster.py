from cobra.steve.util.prelude import *
from cobra.steve.experimental.gcluster.proto import worddata_pb2
from cobra.steve.experimental.gcluster import csvbreaker, workers
from cobra.steve.indexing import protolist

import multiprocessing
import csv


flags.DefineString("aobitu_dir", "/usr/local/google/home/fedele/aobitu/",
                   "The directory of the aobitu output.")
flags.DefineString("tmp_dir", "/tmp/", "Where to write temporary files used in processing.")
flags.DefineInteger("num_shards", 10, "How many shards to use in the output")
flags.DefineInteger("num_workers", 10, "How many workers to run.")
flags.DefineString("chunk_size", 5242880, "How big each file shard is.")
flags.DefineBoolean("append_to_existing_files", False,
                    "If true, append to existing files rather than creating new ones.")

################################################################################
# File Processors
################################################################################


def MakeWordData(terminal):
  worddata = worddata_pb2.WordData()
  worddata.terminal = FixTerminalForProtobufferHack(terminal)
  return worddata


def FixTerminalForProtobufferHack(terminal):
  try:
    unicode(terminal, 'ascii')
  except UnicodeDecodeError:
    return repr(terminal)
  else:
    return terminal


def _TopTerminalsFileProcessorImpl((w1, items), attr):
  worddata = MakeWordData(w1)
  sampled_dist = getattr(worddata, attr)
  for _, w2, count, _ in items:
    sampled_dist.observed_count += 1
    sampled_dist.observed_weight += count
    terminal_count = sampled_dist.terminals.add()
    terminal_count.terminal = FixTerminalForProtobufferHack(w2)
    terminal_count.weight = count
  return worddata


def TopTerminalsAfterFileProcessor(xs):
  return _TopTerminalsFileProcessorImpl(xs, 'terminals_after')


def TopTerminalsBeforeFileProcessor(xs):
  return _TopTerminalsFileProcessorImpl(xs, 'terminals_before')


def PunctuationsFileProcessor((w1, items)):
  worddata = MakeWordData(w1)
  for _, punctuation, count, _ in items:
    terminal_count = worddata.capitalizations.add()
    terminal_count.terminal = FixTerminalForProtobufferHack(punctuation)
    terminal_count.weight = count
  return worddata


def CanonicalPositionsFileProcessor((w1, items)):
  worddata = MakeWordData(w1)
  position_dist = worddata.position_distribution
  for _, pos, count in items:
    setattr(position_dist, pos, count)
  return worddata

def _TotalCountsFileProcessorImpl((w1, count), attr):
  worddata = MakeWordData(w1)
  sampled_dist = getattr(worddata, attr)
  sampled_dist.total_weight = count
  return worddata


def TotalCountsBeforeFileProcessor(xs):
  return _TotalCountsFileProcessorImpl(xs, 'terminals_before')


def TotalCountsAfterFileProcessor(xs):
  return _TotalCountsFileProcessorImpl(xs, 'terminals_after')


def _UniqueCountsFileProcessorImpl((w1, count), attr):
  worddata = MakeWordData(w1)
  sampled_dist = getattr(worddata, attr)
  sampled_dist.total_count = count
  return worddata


def UniqueCountsBeforeFileProcessor(xs):
  return _UniqueCountsFileProcessorImpl(xs, 'terminals_before')


def UniqueCountsAfterFileProcessor(xs):
  return _UniqueCountsFileProcessorImpl(xs, 'terminals_after')


def ShardedTopTerminalsFileProcessor((_2, terminal, count, _1)):
  worddata = MakeWordData(terminal)
  worddata.weight = count
  return worddata


################################################################################
# Multiprocessing Processes
################################################################################


def ProcessorWorker(work_queue, stdout_queue, shard_output_queues):
  while True:
    job = work_queue.get()
    if job is None:
      stdout_queue.put("Worker exiting...")
      break
    try:
      record = None
      processing_function, (path, offsets, group_by_column, integer_columns) = job
      if group_by_column is not None:
        grouper = itemgetter(group_by_column)
      else:
        grouper = None
      record_maker = csvbreaker.ShardedCSVRecordMaker(path, offsets, grouper, integer_columns)
      stdout_queue.put("start processing %s" % record_maker.IdString())
      start_time = time.time()
      num_records_processed = 0
      for record in record_maker:
        worddata = processing_function(record)
        shard = hash(worddata.terminal) % len(shard_output_queues)
        shard_output_queues[shard].put(worddata.SerializeToString())
        num_records_processed += 1
      time_taken = time.time() - start_time
      stdout_queue.put("done processing %s - %d records (%d bytes) in %f seconds" % (record_maker.IdString(),
                                                                                     num_records_processed,
                                                                                     offsets[1] - offsets[0],
                                                                                     time_taken))
    except Exception, e:
      import traceback, StringIO
      exception_string = StringIO.StringIO()
      traceback.print_exc(file=exception_string)
      stdout_queue.put(("EXCEPTION on record %s!\n" % (record,)) +
                       ("while using processor %s\n" % processing_function) +
                       ('*' * 80 + '\n') + exception_string.getvalue() + ('*' * 80 + '\n'))
      exception_string.close()


def main(argv):
  start_time = time.time()

  # Start the process that writes to stdout.
  stdout_queue, stdout_process = workers.StartStdoutWorkerWithQueue()

  # Start the processes that write to the output files.
  shard_output_queues = []
  shard_output_processes = []
  for n in range(FLAGS.num_shards):
    output_path = os.path.join(FLAGS.tmp_dir, "gcluster-preprocess-%d-of-%d.plf" % (n, FLAGS.num_shards))
    queue, process = workers.StartWorddataFileOutputWorkerWithQueue(output_path, FLAGS.append_to_existing_files)
    shard_output_queues.append(queue)
    shard_output_processes.append(process)

  # Start the processes that actually do the processing.
  work_queue = multiprocessing.JoinableQueue()
  worker_processes = []
  for n in range(FLAGS.num_workers):
    worker_process = multiprocessing.Process(target=ProcessorWorker, args=(work_queue, stdout_queue, shard_output_queues))
    worker_processes.append(worker_process)
    worker_process.start()

  # Every file we want to process, along with the processor for it
  file_record_datas = [
      # Path                                                    Processing Function                Group By Col    Integer Columns
      ("output/worddata1/20090806/canonical_positions.csv",     CanonicalPositionsFileProcessor,   0,              [2]),
      ("output/worddata1/20090806/punctuations.csv",            PunctuationsFileProcessor,         0,              [2]),
      ("output/worddata1/20090806/top_terminals_before.csv",    TopTerminalsBeforeFileProcessor,   0,              [2]),
      ("output/worddata1/20090806/top_terminals_after.csv",     TopTerminalsAfterFileProcessor,    0,              [2]),
      ("output/worddata1/20090806/total_counts_before.csv",     TotalCountsBeforeFileProcessor,    None,           [1]),
      ("output/worddata1/20090806/total_counts_after.csv",      TotalCountsAfterFileProcessor,     None,           [1]),
      ("output/worddata1/20090806/unique_terminals_before.csv", UniqueCountsBeforeFileProcessor,   None,           [1]),
      ("output/worddata1/20090806/unique_terminals_after.csv",  UniqueCountsAfterFileProcessor,    None,           [1]),
      ("output/lexicon1/20090806/top_terminals.csv",            ShardedTopTerminalsFileProcessor,  None,           [2]),
      ]

  stdout_queue.put("all workers started in %f seconds" % (time.time() - start_time))

  # Take each file above and generate shards for it, and then dump these onto the work queue.
  for n, (path, processor, group_by_column, integer_columns) in enumerate(file_record_datas):
    absolute_path = os.path.join(FLAGS.aobitu_dir, path)
    # Apparently you can't pass an itemgetter into a subprocess directly...
    grouper = group_by_column and itemgetter(group_by_column) or None
    for m, (start_offset, end_offset) in enumerate(csvbreaker.ShardCSVFile(absolute_path, FLAGS.chunk_size, grouper)):
      file_shard_data = (absolute_path, (start_offset, end_offset), group_by_column, integer_columns)
      work_queue.put((processor, file_shard_data))

  # Put some sentinals in so that the workers stop when all tasks are complete.
  for n in range(FLAGS.num_workers):
    work_queue.put(None)

  stdout_queue.put("finished filling workqueue by %f seconds - waiting for workers to finish..." % (time.time() - start_time))

  # Now, wait for the workers to finish.
  for p in worker_processes:
    p.join()

  stdout_queue.put("All workers are finished at %f seconds, shutting down output..." % (time.time() - start_time))

  # Put sentinals into each of the shard's streams so they know they're done.
  for q in shard_output_queues:
    q.put(None)

  # Now wait for the output processes to finish.
  for p in shard_output_processes:
    p.join()

  stdout_queue.put("All processes shut down, program complete at %f seconds." % (time.time() - start_time))



if __name__ == '__main__':
  app.run()
