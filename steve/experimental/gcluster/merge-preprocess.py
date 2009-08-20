from cobra.steve.util.prelude import *
from cobra.steve.experimental.gcluster.proto import worddata_pb2
from cobra.steve.experimental.gcluster import workers
from cobra.steve.indexing import protolist

import multiprocessing

flags.DefineString("tmp_dir", "/tmp/", "Where to write temporary files used in processing.")
flags.DefineString("input_prefix", "/tmp/gcluster-preprocess", "The common prefix of all input files.")
flags.DefineString("output_file", "/tmp/gcluster-final.plf", "Where to write the final merged output.")
flags.DefineInteger("print_every", 250, "How often to print out progress updates.")
flags.DefineInteger("num_workers", 2, "How many workers to run at once.")



# TODO(fedele): I have a feeling this Worker is general enough to move someplace more common.
def JoinAndMergeFile(stdout_queue, output_queue, file_path_to_process):
  input_list = protolist.ProtoListFile(worddata_pb2.WordData, file_path_to_process, "r")
  grouper = lambda worddata: worddata.terminal
  start_time = time.time()
  stdout_queue.put("reading in %s..." % file_path_to_process)
  sorted_list = list(input_list)
  stdout_queue.put("done reading in in %6.2f seconds, sorting %d records in %s" % (time.time() - start_time,
                                                                                   len(sorted_list), file_path_to_process))
  sort_start_time = time.time()
  sorted_list.sort(key=grouper)
  stdout_queue.put("done sorting %s in %6.2f seconds - merging and output..." % (file_path_to_process, time.time() - sort_start_time))
  num_terminals = num_records = 0
  for terminal, worddatas in groupby(sorted_list, grouper):
    if FLAGS.print_every and num_terminals and num_terminals % FLAGS.print_every == 0:
      stdout_queue.put("%s processed %d terminals - %d / %d records (%6.2f%% complete)" % (file_path_to_process,
                                                                                           num_terminals,
                                                                                           num_records, len(sorted_list),
                                                                                           100 * float(num_records) / len(sorted_list)))
    final_worddata = worddata_pb2.WordData()
    for worddata in worddatas:
      final_worddata.MergeFrom(worddata)
      num_records += 1
    num_terminals += 1
    output_queue.put(final_worddata.SerializeToString())
  stdout_queue.put("%s complete in %6.2f seconds total - %d records for %d terminals" % (file_path_to_process,
                                                                                         time.time() - start_time,
                                                                                         num_records, num_terminals))


def JoinAndMergeWorker(stdout_queue, output_queue, work_queue):
  while True:
    try:
      file_path_to_process = work_queue.get()
      if file_path_to_process is None:
        break
      stdout_queue.put("calling JoinAndMerge on %s" % file_path_to_process)
      JoinAndMergeFile(stdout_queue, output_queue, file_path_to_process)
    except Exception, e:
      import traceback, StringIO
      exception_string = StringIO.StringIO()
      traceback.print_exc(file=exception_string)
      stdout_queue.put(("EXCEPTION while processing %s!\n" % (file_path_to_process,)) +
                       ('*' * 80 + '\n') + exception_string.getvalue() + ('*' * 80 + '\n'))
      exception_string.close()


def main(argv):
  start_time = time.time()

  stdout_queue, stdout_process = workers.StartStdoutWorkerWithQueue()
  output_queue, output_process = workers.StartWorddataFileOutputWorkerWithQueue(FLAGS.output_file)

  work_queue = multiprocessing.JoinableQueue()
  worker_processes = []
  for n in range(FLAGS.num_workers):
    worker = multiprocessing.Process(target=JoinAndMergeWorker, args=(stdout_queue, output_queue, work_queue))
    worker_processes.append(worker)
    worker.start()

  stdout_queue.put("all workers started in %f seconds, loading files into work queue..." % (time.time() - start_time))

  for n, path in enumerate(glob.glob(FLAGS.input_prefix + "*")):
    work_queue.put(path)

  # Finally, a few sentinals to indicate things are done.
  for n in range(FLAGS.num_workers):
    work_queue.put(None)


  for p in worker_processes:
    p.join()

  stdout_queue.put("All workers are finished at %f seconds, shutting down output..." % (time.time() - start_time))
  output_queue.put(None)
  output_process.join()



if __name__ == '__main__':
  app.run()
