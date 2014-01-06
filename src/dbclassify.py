#!/usr/bin/env python2

from classifier import Classifier
from classifier import AllFeatures
from classifier import AllWords
from classifier import Emoticons
from classifier import StopWordFilter
from tweetstore import TweetStore
from aggregator import RetweetWeightedAggregator

import tweet

import getopt
import sys
from datetime import datetime

def usage():
    print("USAGE: %s [-c classifier] [-d database] [-k keyword] [-s 2013-01-31] [-e 2013-03-22]" %
            sys.argv[0])

if __name__ == "__main__":
    db = "tweets"
    keywords = []
    start = datetime(2013, 1, 1)
    end = datetime(2999, 1, 1)

    classifier = "classifier.pickle"

    opts, args = getopt.getopt(sys.argv[1:], "hc:d:k:s:e:")
    for o, a in opts:
        if o == "-d":
            db = a
        elif o == "-c":
            classifier = a
        elif o == "-k":
            keywords.append(a)
        elif o == "-s":
            start = datetime.strptime(a, "%Y-%M-%d")
        elif o == "-e":
            end = datetime.strptime(a, "%Y-%M-%d")
        else:
            usage()
            sys.exit(0)

    classifier = Classifier.load(classifier)
    aggregator = RetweetWeightedAggregator()

    ts = TweetStore(db)
    for t in ts.get(keywords, start, end):
        s = classifier.classify(t)
        print ("%s -- sentiment: %s" % (t[tweet.TEXT],
            "positive" if (s == 1) else "negative"))
        aggregator.add(t, s)

    print ("Aggregated sentiment: %f" % aggregator.get_sentiment())
    print ("ID of last tweet: %d" % aggregator.get_last_id())
    print ("Total number of tweets: %d" % aggregator.get_num())
