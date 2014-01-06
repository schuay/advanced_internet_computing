#!/usr/bin/env python2

import re
import tweet

from nltk.corpus import stopwords

class FeatureSelectionI:
    def select_features(self, obj):
        raise NotImplementedError("Please implement this yourself.")

class AllWords(FeatureSelectionI):
    @staticmethod
    def __get_tweet_features(t):
        """Breaks up text into list of words. Takes a string and returns a dictionary mapping
        word keys to True values."""
        words = re.findall(r"[\w']+|[.,!?;]", t[tweet.TEXT])
        return dict([(word.lower(), True) for word in words])

    def select_features(self, obj):
        return AllWords.__get_tweet_features(obj)

class Emoticons(FeatureSelectionI):
    @staticmethod
    def __get_tweet_features(t):
        """Extracts Emoticons from a string.
        Regex shamelessly copied from http://stackoverflow.com/questions/5862490/how-to-match-emoticons-with-regular-expressions"""
        emoticons = re.findall(r"((?::|;|=)(?:-)?(?:\)|D|P))", t[tweet.TEXT])
        return dict([(emoticon, True) for emoticon in emoticons])

    def select_features(self, obj):
        return Emoticons.__get_tweet_features(obj)

class StopWordFilter(FeatureSelectionI):
    def __init__(self, selection):
        self.__selection = selection
        self.__stopset = StopWordFilter.__stopset()

    def select_features(self, obj):
        fs = self.__selection.select_features(obj);
        return {f: m for f, m in fs.iteritems()
                if (isinstance(f, basestring) and f.lower() not in self.__stopset)}

    @staticmethod
    def __stopset():
        sw = set(stopwords.words('english'))
        meaningful_sw = set([ 'but', 'against', 'off', 'most', 'more', 'few'
                            , 'some', 'no', 'nor', 'not', 'very'])
        return sw - meaningful_sw

class AllHashtags(FeatureSelectionI):
    @staticmethod
    def __get_tweet_features(t):
        words = re.findall(r"#[\w']+", t[tweet.TEXT])
        return dict([(word, True) for word in words])

    def select_features(self, obj):
        return AllHashtags.__get_tweet_features(obj)

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

