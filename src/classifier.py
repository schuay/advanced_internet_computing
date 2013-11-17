#!/bin/python2

import math
import pickle
import re

from nltk.classify import NaiveBayesClassifier, apply_features

NEG = 0
POS = 1

class FeatureSelectionI:
    def select_features(self, obj):
        raise NotImplementedError("Please implement this yourself.")

class AllWords(FeatureSelectionI):
    @staticmethod
    def __get_tweet_features(tweet):
        return AllWords.__get_string_features(tweet["text"])

    """Breaks up text into list of words. Takes a string and returns a dictionary mapping
    word keys to True values."""
    @staticmethod
    def __get_string_features(string):
        words = re.findall(r"[\w']+|[.,!?;]", string)
        return dict([(word, True) for word in words])

    def select_features(self, obj):
        try:
            return AllWords.__get_tweet_features(obj)
        except:
            return AllWords.__get_string_features(obj)

class AllHashtags(FeatureSelectionI):
    @staticmethod
    def __get_tweet_features(tweet):
        return AllHashtags.__get_string_features(tweet["text"])

    @staticmethod
    def __get_string_features(string):
        words = re.findall(r"#[\w']+", string)
        return dict([(word, True) for word in words])

    def select_features(self, obj):
        try:
            return AllHashtags.__get_tweet_features(obj)
        except:
            return AllHashtags.__get_string_features(obj)

"""Applies the feature selections in list that yields features."""
class AnyFeatures(FeatureSelectionI):
    def __init__(self, selections):
	self.__selections = selections;

    def select_features(self, obj):
        for sel in self.__selections:
            features = sel.select_features(obj)
            if (features):
                return features

        return dict()

"""Applies all feature selections in list.
If two methods yield the same feature, the last one is used."""
class AllFeatures(FeatureSelectionI):
    def __init__(self, selections):
	self.__selections = selections;

    def select_features(self, obj):
        features = dict()
        for sel in self.__selections:
            features.update(sel.select_features(obj))

        return features

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
    def train(training_sets, feature_selection=AllWords()):
        training = []

        # Since we have a rather large amount of training data, build features
        # lazily to avoid running out of memory.
        tuple_set = [(x, cl) for cl in [POS, NEG]
                             for x in training_sets[cl]]
        train_set = apply_features(feature_selection.select_features, tuple_set)

        return Classifier(NaiveBayesClassifier.train(train_set), feature_selection, len(tuple_set))

    """Evaluates the classifier with the given data sets."""
    def evaluate(self, test_sets):
        tuple_set = [(x, cl) for cl in [POS, NEG]
                             for x in test_sets[cl]]
        test_set = apply_features(self.__fs.select_features, tuple_set)

        referenceSets = [set() for x in [POS, NEG]]
        testSets = [set() for x in [POS, NEG]]
        for i, (tweet, label) in enumerate(tuple_set):
            referenceSets[label].add(i)
            predicted = self.classify(tweet)
            testSets[predicted].add(i)

        print 'train on %d instances, test on %d instances' % (self.__train_size, len(tuple_set))
        print 'accuracy:', nltk.classify.util.accuracy(self.__nltk_classifier, test_set)
        print 'pos precision:', nltk.metrics.precision(referenceSets[POS], testSets[POS])
        print 'pos recall:', nltk.metrics.recall(referenceSets[POS], testSets[POS])
        print 'neg precision:', nltk.metrics.precision(referenceSets[NEG], testSets[NEG])
        print 'neg recall:', nltk.metrics.recall(referenceSets[NEG], testSets[NEG])

    def classify(self, obj):
        features = self.__fs.select_features(obj)
        return self.__nltk_classifier.classify(features)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

import getopt
import nltk
import sys

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

        classifier = Classifier.train(trainSets, AllWords());

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
