#!/bin/python2

import json
import math
import pickle
import re

from nltk.classify import NaiveBayesClassifier

class Classifier:
    class Sentiment:
        NEGATIVE = 0
        POSITIVE = 1

    assert Sentiment.NEGATIVE == 0
    assert Sentiment.POSITIVE == 1

    __pos = Sentiment.POSITIVE
    __neg = Sentiment.NEGATIVE

    def __init__(self, classifier):
        self._nltk_classifier = classifier

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def train(training_sets):
        training = []

        for i in training_sets[Classifier.__pos]:
            if isinstance(i, str):
                features = [Classifier.__get_string_features(i), Classifier.__pos]
            # TODO: do for other input
            training.append(features)

        for i in training_sets[Classifier.__neg]:
            if isinstance(i, str):
                features = [Classifier.__get_string_features(i), Classifier.__neg]
            # TODO: do for other input
            training.append(features)

        return Classifier(NaiveBayesClassifier.train(training))

    @staticmethod
    def __get_tweet_features(tweet):
        # TODO: parse json and call __get_string_features with the tweet text.
        pass

    @staticmethod
    def __get_string_features(string):
	# simply break up text into list of words
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
    pos = Classifier.Sentiment.POSITIVE
    neg = Classifier.Sentiment.NEGATIVE

    with open(positive, 'r') as f:
        posTweets = re.split(r'\n', f.read())
    with open(negative, 'r') as f:
        negTweets = re.split(r'\n', f.read())
 
    #selects 3/4 of the features to be used for training and 1/4 to be used for testing
    posCutoff = int(math.floor(len(posTweets)*3/4))
    negCutoff = int(math.floor(len(negTweets)*3/4))

    trainSets = [list() for x in [pos, neg]]
    trainSets[pos] = posTweets[:posCutoff]
    trainSets[neg] = negTweets[:negCutoff]
    nTrain = len(trainSets[pos]) + len(trainSets[neg])

    if load:
        print 'loading classifier \'%s\'' % load
        classifier = Classifier.load(load)
    else:
        print 'training new classifier'
        classifier = Classifier.train(trainSets);

    if save:
        print 'saving classifier as \'%s\'' % save
        classifier.save(save)

    print 'testing classifier...'
    testTweets = []
    testFeatures = []
    for i in posTweets[posCutoff:]:
        words = re.findall(r"[\w']+|[.,!?;]", i)
        tweetFeatures = [dict([(word, True) for word in words]), pos]
        testFeatures.append(tweetFeatures)

        t = [i, pos]
        testTweets.append(t)
    for i in negTweets[negCutoff:]:
        words = re.findall(r"[\w']+|[.,!?;]", i)
        tweetFeatures = [dict([(word, True) for word in words]), neg]
        testFeatures.append(tweetFeatures)

        t = [i, neg]
        testTweets.append(t)

    referenceSets = [set() for x in [pos, neg]]
    testSets = [set() for x in [pos, neg]]
    for i, (tweet, label) in enumerate(testTweets):
        referenceSets[label].add(i)
        predicted = classifier.classify_string(tweet)
        testSets[predicted].add(i)

    classifier = classifier._nltk_classifier
    print 'train on %d instances, test on %d instances' % (nTrain, len(testTweets))
    print 'accuracy:', nltk.classify.util.accuracy(classifier, testFeatures)
    print 'pos precision:', nltk.metrics.precision(referenceSets[pos], testSets[pos])
    print 'pos recall:', nltk.metrics.recall(referenceSets[pos], testSets[pos])
    print 'neg precision:', nltk.metrics.precision(referenceSets[neg], testSets[neg])
    print 'neg recall:', nltk.metrics.recall(referenceSets[neg], testSets[neg])

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
