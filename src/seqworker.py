import Queue
import task

from threading import Thread
from classifier import Classifier
from classifier import AllWords
from aggregator import MeanAggregator

GET_TIMEOUT = 0.1

class SeqWorker(Thread):
    """task_queue: Queue; db_name: string; classifier: Classifier"""
    def __init__(self, task_queue, db_name, classifier):
        super(SeqWorker, self).__init__()
        self.__task_queue = task_queue
        self.__db_name = db_name
        self.__classifier = classifier
        self.keep_working = True

    def run(self):
        q = self.__task_queue

        while self.keep_working:
            t = None
            while t is None:
                try:
                    if not self.keep_working:
                        print "Worker terminating by request"
                        return
                    t = q.get(timeout = GET_TIMEOUT)
                except Queue.Empty:
                    pass

            task.run(t, self.__classifier, MeanAggregator())
            q.task_done()
