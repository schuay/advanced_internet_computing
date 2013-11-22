from threading import Thread
from classifier import Classifier
from classifier import AllWords
from aggregator import MeanAggregator

class SeqWorker(Thread):
    def __init__(self, task_queue, db_name, classifier):
        super(SeqWorker, self).__init__()
        self.__task_queue = task_queue
        self.__db_name = db_name
        self.__classifier = classifier

    def run(self):
        pass
