#/usr/bin/python

import pandas as pd
import numpy as np
import datetime
import os,sys
from unbalanced_dataset import SMOTE

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# read airport and carrier information
arpt = pd.read_csv("airports_lookup.csv")
arlne = pd.read_csv("carriers_lookup.csv")
arpt['Dest'] = arpt['iata']
arpt['aid'] = arpt['id']
arlne['UniqueCarrier'] = arlne['Code']
arlne['cid'] = arlne['id']
oarpt = pd.DataFrame(columns=['oid','Origin'])
oarpt['Origin'] = arpt['Dest']
oarpt['oid'] = arpt['aid']

print "supplemental files loaded."

# read data about delays into dataframe and manipulate it to get results
yrs = range(2006, 2009)

# function to create status column
def getDel(row):
    if row['ArrDelay'] <= 0:
        return 0.0
    else:
        return 1.0

# function to remove nulls where ind is the parameter which determines if a dataset is for training or prediction purposes
def rmnulls(dat, yr, ind):
  if ind == 0:
        if (len(dat[(dat['Year'] == yrs[0]) & (dat['ArrDelay'].isnull())])/float(len(dat[dat['Year'] == yrs[0]]))) * 100 > 5:
            print "may lose more than 2% data of year %s if nulls are removed." % yr
        else:
            redata = dat[(dat['Year'] == yrs[0]) & (dat['ArrDelay'].notnull())]
        if (len(dat[(dat['Year'] == yr) & (dat['ArrDelay'].isnull())])/float(len(dat[dat['Year'] == yr])))* 100 > 5:
            print "may lose more than 2% data of year %s if nulls are removed." % yr
        else:
            redata = pd.concat((redata, dat[(dat['Year'] == yr) & (dat['ArrDelay'].notnull())]), axis=0)
  else:
        if (len(dat[(dat['Year'] == yr) & (dat['ArrDelay'].isnull())])/float(len(dat[dat['Year'] == yr]))) * 100 > 5:
            print "may lose more than 2% data if nulls are removed." 
        else:
            redata = dat[(dat['Year'] == yr) & (dat['ArrDelay'].notnull())]
 
  return redata

def mergeInfo(dat):
  dataf = dat.merge(arpt[['Dest','aid']], on='Dest', how='left')
  datafna = dataf.merge(arlne[['UniqueCarrier','cid']], on='UniqueCarrier', how='left')
  datafullna = datafna.merge(oarpt[['Origin','oid']], on='Origin', how='left')

  return datafullna

def transformData(en, dat):
  x_data = en.transform(dat)
 
  return x_data

def classifyData(cl, dat):
  predv = cl.predict(dat)
  return predv

def testTrain(yr):
  data = pd.read_csv(str(yr[0]) + '.csv.bz2', compression='bz2', header=0, sep=',')
  print "loading %s year" % yr[0]

  trainyrs = 2
 
  for i in range(len(yr)):
    if i != 0:
      if i < trainyrs:
	print "loading %s year" % yr[i]
    	fl = str(yr[i]) + '.csv.bz2'
    	df = pd.read_csv(fl, compression='bz2', header=0, sep=',')
	data = pd.concat((data, df), axis=0)
      if i == trainyrs:
        data = pd.read_csv(str(yr[i]) + '.csv.bz2', compression='bz2', header=0, sep=',')
        print "loading %s year" % yr[i]

      print "merge data with airport and airline data"
      #datanew = data[(data['Dest'] == "DAL") | (data['Dest'] == "DFW")]
      datafullna = mergeInfo(datanew)
   
      print "Data loaded."
 
      # remove nulls
      if i < trainyrs:
         datafull = rmnulls(datafullna, yr[i], 0)
      elif i == trainyrs:
         datafull = rmnulls(datafullna, yr[i], 1)

      dfa = datafull[['Year','Month','DayOfWeek','cid','aid','oid','ArrDelay']]
      dfa.is_copy = False
    
      print "creating status column"

      dfa['status'] = dfa.apply(lambda row: getDel(row), axis=1)
      
      print "ratio of delays: %s, ratio of on-time flights: %s" % ((float(len(dfa[dfa.status == 1]))/len(dfa)), (float(len(dfa[dfa.status == 0]))/len(dfa)))
      print "actually transforming data"

      datax = dfa[['Month','DayOfWeek','cid','aid','oid']]

      data_y = dfa['status'].values
    
      print "using onehotencoder"
     
      if i < trainyrs:
          from sklearn.preprocessing import OneHotEncoder

          enc = OneHotEncoder(handle_unknown='ignore')
          data_x = enc.fit_transform(datax) 
      elif i == trainyrs:
          data_x = transformData(enc, datax) 
    
      print "running SGDClassifier"
    
      if i < trainyrs: 
        from sklearn.linear_model import SGDClassifier
        clf = SGDClassifier(loss="hinge",shuffle=True,class_weight="auto")    
        print "fitting data"
        sys.stdout.flush() 
        clf.fit(data_x, data_y)
        print "fitted data"
      elif i == trainyrs:
        from sklearn.metrics import accuracy_score 
        from sklearn.metrics import f1_score
        from sklearn.metrics import confusion_matrix
        #from sklearn import metrics 
        pred = classifyData(clf, data_x)
        accuracy = accuracy_score(data_y, pred)
        f1 = f1_score(data_y, pred)
        confusion = confusion_matrix(data_y, pred)
        #fpr, tpr, thresh = metrics.roc_curve(data_y, pred, pos_label=1)
        #auc_value = metrics.auc(fpr, tpr) 
        #print "accuracy score: %s f1-score : %s confusion_matrix: %s area_under_curve: %s" % (accuracy, f1, confusion, auc_value)
        print "accuracy score: %s f1-score : %s confusion_matrix: %s" % (accuracy, f1, confusion)
        print "testing value: %s" % data_y[4]
  
  return enc, clf, pred

ohenc, sgdclf, pred = testTrain(yrs)

print "predicted value: %s" % pred[4]

while True:
      dest = raw_input("Please enter the Origin airport code (eg. DFW for Dallas Fort-worth):")
      origin = raw_input("\nPlease enter the Destination airport code (it should be the flight destination which may be a stop-over):")
      fldate = raw_input("\nPlease enter the date of the flight (MM/DD/YYYY):")
      carr = raw_input("\nPlease enter the airline:")
      
      userdf = pd.DataFrame(columns=("Month","DayOfWeek","UniqueCarrier","Dest","Origin"))
      dttup = datetime.datetime.strptime(fldate, "%m/%d/%Y")
      mon = dttup.month 
      daywk = dttup.weekday() + 1
      #userdf['Month'] = mon
      userdf = pd.DataFrame({"Month":[mon],"DayOfWeek":[daywk],"UniqueCarrier":[carr],"Dest":[dest],"Origin":[origin]})
      #userdf['DayOfWeek'] = daywk
      #userdf['UniqueCarrier'] = carr
      #userdf['Dest'] = dest
      #userdf['Origin'] = origin
     
      print userdf 
      usrdata = mergeInfo(userdf) 
      print usrdata
      usrdata = usrdata[['Month','DayOfWeek','cid','aid','oid']]
      usrdat_x = transformData(ohenc, usrdata)
      usrpred = classifyData(sgdclf, usrdat_x)
      
      print "The flight will be %s (0 = on-time, 1 = delayed)" % usrpred 
