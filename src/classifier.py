#!/bin/python2

import json
import math
import pickle
import re

from nltk.classify import NaiveBayesClassifier, apply_features

NEG = 0
POS = 1

class Classifier:
    def __init__(self, classifier):
        self._nltk_classifier = classifier

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    """Takes a dictionary with keys: POSITIVE/NEGATIVE, values: list of
    individual tweets. Returns a classifier object trained on the given training sets."""
    @staticmethod
    def train(training_sets):
        training = []

        # Since we have a rather large amount of training data, build features
        # lazily to avoid running out of memory.
        tuple_set = [(x, cl) for cl in [POS, NEG]
                             for x in training_sets[cl]]
        train_set = apply_features(Classifier.__get_string_features, tuple_set)

        return Classifier(NaiveBayesClassifier.train(train_set))

    @staticmethod
    def __get_tweet_features(tweet):
        # TODO: parse json and call __get_string_features with the tweet text.
        pass

    """Breaks up text into list of words. Takes a string and returns a dictionary mapping
    word keys to True values."""
    @staticmethod
    def __get_string_features(string):
        words = re.findall(r"[\w']+|[.,!?;]", string)
        return dict([(word, True) for word in words])

    def __classify_features(self, features):
        return self._nltk_classifier.classify(features)

    def classify_string(self, string):
        features = Classifier.__get_string_features(string)
        return self.__classify_features(features)

    def classify_tweet(self, tweet):
        features = Classifier.__get_tweet_features(tweet)
        return self.__classify_features(features)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

import getopt
import nltk
import sys

from tweetstore import TweetStore

def evaluate_features(positive, negative, load, save):
    with open(positive, 'r') as f:
        posTweets = re.split(r'\n', f.read())
    with open(negative, 'r') as f:
        negTweets = re.split(r'\n', f.read())
 
    #selects 3/4 of the features to be used for training and 1/4 to be used for testing
    posCutoff = int(math.floor(len(posTweets)*3/4))
    negCutoff = int(math.floor(len(negTweets)*3/4))

    if load:
        print 'loading classifier \'%s\'' % load
        classifier = Classifier.load(load)
    else:
        print 'training new classifier'

        trainSets = [list() for x in [POS, NEG]]
        trainSets[POS] = posTweets[:posCutoff]
        trainSets[NEG] = negTweets[:negCutoff]
        nTrain = len(trainSets[POS]) + len(trainSets[NEG])

        classifier = Classifier.train(trainSets);

        trainSets = None

    if save:
        print 'saving classifier as \'%s\'' % save
        classifier.save(save)

    print 'testing classifier...'
    testTweets = []
    testFeatures = []
    for i in posTweets[posCutoff:]:
        words = re.findall(r"[\w']+|[.,!?;]", i)
        tweetFeatures = [dict([(word, True) for word in words]), POS]
        testFeatures.append(tweetFeatures)

        t = [i, POS]
        testTweets.append(t)
    for i in negTweets[negCutoff:]:
        words = re.findall(r"[\w']+|[.,!?;]", i)
        tweetFeatures = [dict([(word, True) for word in words]), NEG]
        testFeatures.append(tweetFeatures)

        t = [i, NEG]
        testTweets.append(t)

    referenceSets = [set() for x in [POS, NEG]]
    testSets = [set() for x in [POS, NEG]]
    for i, (tweet, label) in enumerate(testTweets):
        referenceSets[label].add(i)
        predicted = classifier.classify_string(tweet)
        testSets[predicted].add(i)

    classifier = classifier._nltk_classifier
    print 'train on %d instances, test on %d instances' % (nTrain, len(testTweets))
    print 'accuracy:', nltk.classify.util.accuracy(classifier, testFeatures)
    print 'pos precision:', nltk.metrics.precision(referenceSets[POS], testSets[POS])
    print 'pos recall:', nltk.metrics.recall(referenceSets[POS], testSets[POS])
    print 'neg precision:', nltk.metrics.precision(referenceSets[NEG], testSets[NEG])
    print 'neg recall:', nltk.metrics.recall(referenceSets[NEG], testSets[NEG])

def usage():
    print("USAGE: %s [-p positive_tweets] [-n negative_tweets] [-s classifier] [-l classifier]" %
            sys.argv[0])

if __name__ == '__main__':
    classifier_save = None
    classifier_load = None

    positive_file = 'sentiment.pos'
    negative_file = 'sentiment.neg'

    opts, args = getopt.getopt(sys.argv[1:], "hs:l:p:n:")
    for o, a in opts:
        if o == "-s":
            classifier_save = a
        elif o == "-l":
            classifier_load = a
        elif o == "-p":
            positive_file = a
        elif o == "-n":
            negative_file = a
        else:
            usage()
            sys.exit(0)

    evaluate_features(positive_file,
                      negative_file,
                      classifier_load,
                      classifier_save)
