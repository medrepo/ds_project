#!/usr/bin/python


"""
    Starter code for the evaluation mini-project.
    Start by copying your trained/tested POI identifier from
    that which you built in the validation mini-project.

    This is the second step toward building your POI identifier!

    Start by loading/formatting the data...
"""

import pickle
import sys
from sklearn.cross_validation import train_test_split

sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit

data_dict = pickle.load(open("../final_project/final_project_dataset.pkl", "r") )

### add more features to features_list!
features_list = ["poi", "salary"]

data = featureFormat(data_dict, features_list)
labels, features = targetFeatureSplit(data)



### your code goes here 
# split training and testing data
features_train, features_test, labels_train, labels_test = train_test_split(features, labels, test_size=0.3, random_state=42)

from sklearn.tree import DecisionTreeClassifier
clf = DecisionTreeClassifier()
clf.fit(features_train, labels_train)

accuracy = round(clf.score(features_test, labels_test), 4)

print "The accuracy for the decision tree classifier is %s" % accuracy

# number of POIs in test set
eval = clf.predict(features_test, labels_test)
cnt = 0
poscnt = 0

for x in range(len(eval)):
	if eval[x] == 1.:
		cnt += 1 
		if labels_test[x] == 1.:
			poscnt += 1			


print "Out of %s total people in test set, the number of POIs in test set is %s" % (len(eval), cnt) 

print "The number of true positives is %s" % poscnt

# precision score and recall score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score 

precision = round(precision_score(labels_test, eval, average='weighted'), 2)
recall = round(recall_score(labels_test, eval, average='weighted'), 2)

print "The precision score is %s and \nthe recall score is %s" % (precision, recall)

# evaluate the confusion matrix for fictitious data
predictions = [0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1]
true_labels = [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0]

def count(val, valtrue, pred, true):
	cnt = 0	
	for x in range(len(pred)):
		if pred[x] == val and true[x] == valtrue:
			cnt += 1
	return cnt

truepos = count(1, 1, predictions, true_labels)
falsepos = count(1, 0, predictions, true_labels)
trueneg = count(0, 0, predictions, true_labels)
falseneg = count(0, 1, predictions, true_labels)

print "# of true positives = %s \n # of false positives = %s \n # of true negatives = %s \n # of false negatives = %s" % (truepos, falsepos, trueneg, falseneg) 

# precision and recall of this fictitious classifier
prec = round(precision_score(true_labels, predictions, average='weighted'), 2)
rec = round(recall_score(true_labels, predictions, average='weighted'), 2)

print "The precision is %s and recall is %s" % (prec, rec)

