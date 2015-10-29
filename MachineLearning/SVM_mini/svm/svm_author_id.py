#!/usr/bin/python

""" 
    This is the code to accompany the Lesson 2 (SVM) mini-project.

    Use a SVM to identify emails from the Enron corpus by their authors:    
    Sara has label 0
    Chris has label 1
"""
    
import sys
from time import time
sys.path.append("../tools/")
from email_preprocess import preprocess


### features_train and features_test are the features for the training
### and testing datasets, respectively
### labels_train and labels_test are the corresponding item labels
features_train, features_test, labels_train, labels_test = preprocess()




#########################################################
### your code goes here ###

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

"""# comparing different values for C
cval = (10.0, 100.0, 1000.0, 10000.0)

#clf = SVC(kernel="linear")"""

# train with only 1% data
#features_train = features_train[:len(features_train)/100]
#labels_train = labels_train[:len(labels_train)/100]

"""for x in range(len(cval)): 
	clf = SVC(kernel="rbf", C=cval[x])

	# print c value
	print "C = ", cval[x]

	# calculate time to train and train
	t0 = time()
	clf.fit(features_train, labels_train)
	print "training time: ",round(time()-t0,3),"s"

	# calculate prediction time and predict
	t1 = time()
	pred = clf.predict(features_test)
	print "prediction time: ",round(time()-t1,3),"s"

	# compute accuracy of classification
	accuracy = round(accuracy_score(pred, labels_test) * 100, 2)

	print "The Accuracy of the SVC classifier = %s%%" % accuracy

	# capture C with best accuracy 
	laccuracy = 0
	if accuracy >= laccuracy:
		laccuracy = accuracy
		bestc = cval[x]
	
print "The best accuracy is for C = ",bestc," with a value of %s" % laccuracy"""

# use optimized SVM
cval = 10000.0

clf = SVC(kernel="rbf", C=cval)

# print c value
print "C = ",cval

# calculate time to train and train
t0 = time()
clf.fit(features_train, labels_train)
print "training time: ",round(time()-t0,3),"s"

# calculate prediction time and predict

# array of element numbers to predict from the test set 
pval = (10,26,50)

t1 = time()
pred = clf.predict(features_test)
print "prediction time: ",round(time()-t1,3),"s"

for x in range(len(pval)):
	print "The class for the ",pval[x],"th test element is ",pred[pval[x]]

# function to calculate number of predictions per classification label
def numclass(predvar, classval):
	cnt = 0	
	for x in range(len(predvar)):
		if predvar[x] == classval:
			cnt += 1
	return cnt

countclass = 1
	
print "The number of test events predicted to be in \"Chris\" (1) class = %s" % numclass(pred, countclass)

"""# compute accuracy of classification
accuracy = round(accuracy_score(pred, labels_test) * 100, 2)

print "The Accuracy of the optimized SVC classifier = %s%%" % accuracy """

#########################################################


