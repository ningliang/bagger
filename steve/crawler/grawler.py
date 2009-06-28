from multiprocessing import Process, Queue, Pool


from cobra.steve.util.prelude import *


def TwistedFetchingProcess(url_queue, processor_pool):
  while True:
    url, callback = url_queue.get()
    getPage(url).addCallback(lambda v: processor_pool.apply_async(callback, v))


def main(argv):
  url_queue = Queue()
  processor_pool = Pool()
  fetcher = Process(target=TwistedFetchingProcess, args=(url_queue, processor_pool))
  
  
  pass


if __name__ == '__main__':
  app.run()