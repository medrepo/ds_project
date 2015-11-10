#!/usr/bin/python

import pickle
import numpy
numpy.random.seed(42)


### The words (features) and authors (labels), already largely processed.
### These files should have been created from the previous (Lesson 10)
### mini-project.
words_file = "../text_learning/your_word_data.pkl" 
authors_file = "../text_learning/your_email_authors.pkl"
word_data = pickle.load( open(words_file, "r"))
authors = pickle.load( open(authors_file, "r") )



### test_size is the percentage of events assigned to the test set (the
### remainder go into training)
### feature matrices changed to dense representations for compatibility with
### classifier functions in versions 0.15.2 and earlier
from sklearn import cross_validation
features_train, features_test, labels_train, labels_test = cross_validation.train_test_split(word_data, authors, test_size=0.1, random_state=42)

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                             stop_words='english')
features_train = vectorizer.fit_transform(features_train)
features_test = vectorizer.transform(features_test).toarray()


### a classic way to overfit is to use a small number
### of data points and a large number of features;
### train on only 150 events to put ourselves in this regime
features_train = features_train[:150].toarray()
labels_train = labels_train[:150]



### your code goes here
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

clf = DecisionTreeClassifier(min_samples_split=40)
clf.fit(features_train, labels_train)

pred = clf.predict(features_test)

acc = accuracy_score(labels_test, pred)

print "The accuracy is %s" % round(acc, 3)

print "Number of training points are %s" % len(features_train)

# evaluate the importance of each feature
feat = clf.feature_importances_

imp = feat[0]
# to get all remaining words causing discrimination
impwords = []

for i in range(len(feat)):
	if feat[i] > 0.2:
		impwords.insert(i, vectorizer.get_feature_names()[i]) 
		
		# to find the most important features	
		if feat[i] > imp:
			imp = feat[i]
			impx = i
			#impword = vectorizer.get_feature_names()[i] 
 
print "the most important feature is the %s number feature with an importance of %s" % (impx, round(imp, 4))
#print "The word causing the most discrimination is %s" % impword
print "The words/word causing the most discrimination are/is %s" % impwords
