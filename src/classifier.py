#!/usr/bin/env python2

import math
import cPickle as pickle
import re

import featureselection as fs
import tweet

from nltk.classify import NaiveBayesClassifier
from nltk.classify import SklearnClassifier
from nltk.classify.util import apply_features
from sklearn.svm import LinearSVC

NEG = 0
POS = 1

CLASSIFIERS = { 'bayes': NaiveBayesClassifier
              , 'svm':   SklearnClassifier(LinearSVC())
              }

class Classifier:
    def __init__(self, classifier, feature_selection, train_size):
        self.__nltk_classifier = classifier
        self.__fs = feature_selection
        self.__train_size = train_size

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    """Takes a dictionary with keys: POSITIVE/NEGATIVE, values: list of
    individual tweets. Returns a classifier object trained on the given training sets."""
    @staticmethod
    def train(raw_classifier, training_sets, feature_selection = fs.AllWords()):
        training = []

        # Since we have a rather large amount of training data, build features
        # lazily to avoid running out of memory.
        tuple_set = [(x, cl) for cl in [POS, NEG]
                             for x in training_sets[cl]]
        train_set = apply_features(feature_selection.select_features, tuple_set)

        return Classifier(raw_classifier.train(train_set), feature_selection, len(tuple_set))

    """Evaluates the classifier with the given data sets."""
    def evaluate(self, test_sets):
        tuple_set = [(x, cl) for cl in [POS, NEG]
                             for x in test_sets[cl]]
        test_set = apply_features(self.__fs.select_features, tuple_set)

        referenceSets = [set() for x in [POS, NEG]]
        testSets = [set() for x in [POS, NEG]]
        for i, (t, label) in enumerate(tuple_set):
            referenceSets[label].add(i)
            predicted = self.classify(t)
            testSets[predicted].add(i)

        print 'train on %d instances, test on %d instances' % (self.__train_size, len(tuple_set))
        print 'accuracy:', nltk.classify.util.accuracy(self.__nltk_classifier, test_set)
        print 'pos precision:', nltk.metrics.precision(referenceSets[POS], testSets[POS])
        print 'pos recall:', nltk.metrics.recall(referenceSets[POS], testSets[POS])
        print 'neg precision:', nltk.metrics.precision(referenceSets[NEG], testSets[NEG])
        print 'neg recall:', nltk.metrics.recall(referenceSets[NEG], testSets[NEG])

        try:
            print self.__nltk_classifier.show_most_informative_features(10)
        except AttributeError:
            pass # Not all classifiers provide this function.


    def classify(self, obj):
        features = self.__fs.select_features(obj)
        return self.__nltk_classifier.classify(features)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

import getopt
import nltk
import re
import sys

def prefilter(tweets):
    PATTERN_SPAM1 = re.compile("Get 100 followers a day")
    PATTERN_SPAM2 = re.compile("I highly recommends you join www.m2e.asia")

    FILTERS = [ lambda t: not PATTERN_SPAM1.search(t)
              , lambda t: not PATTERN_SPAM2.search(t)
              ]

    return filter(lambda t: all([f(t[tweet.TEXT]) for f in FILTERS]), tweets)

def to_tweets(lines):
    """Turns a list of tweet texts into a list of tweet dict objects."""
    return [{tweet.TEXT: t} for t in lines]

def evaluate_features(positive, negative, load, save, cutoff,
                      stopWordFilter, raw_classifier):
    with open(positive, 'r') as f:
        posTweets = prefilter(to_tweets(re.split(r'\n', f.read())))
    with open(negative, 'r') as f:
        negTweets = prefilter(to_tweets(re.split(r'\n', f.read())))
 
    # Selects cutoff of the features to be used for training and (1 - cutoff)
    # to be used for testing.
    posCutoff = int(math.floor(len(posTweets)*cutoff))
    negCutoff = int(math.floor(len(negTweets)*cutoff))

    if load:
        print 'loading classifier \'%s\'' % load
        classifier = Classifier.load(load)

    else:
        print 'training new classifier'

        trainSets = [list() for x in [POS, NEG]]
        trainSets[POS] = posTweets[:posCutoff]
        trainSets[NEG] = negTweets[:negCutoff]

        featureSelection = fs.AllWords()
        if stopWordFilter:
            print 'using stop words filter'
            featureSelection = fs.StopWordFilter(featureSelection)
        featureSelection = fs.AllFeatures([fs.Emoticons(), featureSelection])

        classifier = Classifier.train(raw_classifier, trainSets, featureSelection);

        trainSets = None

    if save:
        print 'saving classifier as \'%s\'' % save

        classifier.save(save)

    print 'testing classifier...'

    trainSets = [list() for x in [POS, NEG]]
    trainSets[POS] = posTweets[posCutoff:]
    trainSets[NEG] = negTweets[negCutoff:]
    classifier.evaluate(trainSets)


def usage():
    print("""USAGE: %s [-p positive_tweets] [-n negative_tweets] [-s classifier] [-l classifier] [-c training cutoff] [-w]
            -p  Text file containing one positive tweet per line.
            -n  Text file containing one negative tweet per line.
            -s  Saves the classifier to the specified file.
            -l  Loads the classifier from the specified file.
            -c  Specifies the percentage of training tweets (default = 0.75).
            -w  Enables the stopword filter (default = False).
            -t  Selects the classifier type. One of 'bayes', 'svm' (default).""" %
            sys.argv[0])
    sys.exit(1)

# TODO: Since we now need to download nltk stopwords, mention this in the readme
# or implement automatic downloading into a local dir within this script.

if __name__ == '__main__':
    classifier_save = None
    classifier_load = None

    positive_file = 'sentiment.pos'
    negative_file = 'sentiment.neg'
    stopWordFilter = False
    cutoff = 0.75
    raw_classifier = CLASSIFIERS['svm']

    opts, args = getopt.getopt(sys.argv[1:], "hc:s:l:p:n:c:wt:")
    for o, a in opts:
        if o == "-s":
            classifier_save = a
        elif o == "-l":
            classifier_load = a
        elif o == "-p":
            positive_file = a
        elif o == "-n":
            negative_file = a
        elif o == "-c":
            cutoff = float(a)
        elif o == "-w":
            stopWordFilter = True
        elif o == "-t":
            if not a in CLASSIFIERS:
                usage()
            raw_classifier = CLASSIFIERS[a]
        else:
            usage()

    evaluate_features(positive_file,
                      negative_file,
                      classifier_load,
                      classifier_save,
                      cutoff,
                      stopWordFilter,
                      raw_classifier)
