# needs to copy the files good.txt and bad.txt from dropbox into the folder
# the classifier is not really precise (about 0.5)
# example for saving and reopen (reopen_naivebayes.py)

import nltk
import random
import pickle

fg = open ('good.txt', 'r');
fb = open ('bad.txt', 'r');
print('read data...')
sentiment =([(line, 'good') for line in fg] + 
    [(line, 'bad') for line in fb])
		 
fg.close()
fb.close()
print('finished reading data')
random.shuffle(sentiment);

def sentiment_features(line):
	#-1 to cut the '\n'
    return{'sentiment':line[0:-1].lower()}

featuresets = [(sentiment_features(n), g) for (n,g) in sentiment]

length = len(sentiment)
#half = length/2
third = length/3

#train_set, test_set = featuresets[half:], featuresets[:half]
#maybe better performance with 2/3 training set?
train_set, test_set = featuresets[2*third:], featuresets[:third]
print('trying to train...')
classifier = nltk.NaiveBayesClassifier.train(train_set);

print('try to classifiy its super')
print(classifier.classify({'sentiment':'it\'s super'}))
print('try to classifiy its bad')
print(classifier.classify({'sentiment':'it\'s bad'}))

print('accuracy:')
print nltk.classify.accuracy(classifier, test_set)
print classifier.show_most_informative_features(5)

f = open('naive_bayes_classifier_1.pickle', 'wb')
pickle.dump(classifier, f)
f.close();

print('done')