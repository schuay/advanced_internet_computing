import pickle
import nltk

f = open('naive_bayes_classifier_1.pickle')
classifier = pickle.load(f)
f.close()

print('try to classifiy its super')
print(classifier.classify({'sentiment':'it\'s super'}))
print('try to classifiy its bad')
print(classifier.classify({'sentiment':'it\'s bad'}))
