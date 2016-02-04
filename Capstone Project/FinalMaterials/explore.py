#/usr/bin/python

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm 
import sys

# convert airports and carrier information into dataframe
arpt = pd.read_csv("airports.csv")
arlne = pd.read_csv("carriers.csv")
arpt['location'] = arpt['city'] + ", " + arpt['state']
arpt['Dest'] = arpt['iata']
arlne['UniqueCarrier'] = arlne['Code']
arlne['Description'] = arlne['Description'].str.replace(r'\(.*\)', '')

# create day dataframe
daysdf = pd.read_csv("days_map.csv", header=0, sep=',')
print daysdf
sys.stdout.flush()

print "supplemental files loaded."
sys.stdout.flush()

# read data about delays into dataframe and manipulate it to get results
yr = range(2006, 2009)

data = pd.read_csv(str(yr[0]) + '.csv.bz2', compression='bz2', header=0, sep=',')

for x in range(len(yr)):
    if x != 0:
	print "loading %s year" % yr[x]
	sys.stdout.flush()	
    	fl = str(yr[x]) + '.csv.bz2'
    	df = pd.read_csv(fl, compression='bz2', header=0, sep=',')
	data = pd.concat((data, df), axis=0)

#data = datafull[datafull.ArrDelay > 0]
print "merge data with airport and airline data"
sys.stdout.flush()

dataf = data.merge(arpt[['Dest','location']], on='Dest', how='left')
datafullna = dataf.merge(arlne[['UniqueCarrier','Description']], on='UniqueCarrier', how='left')

print "data loaded." 
sys.stdout.flush()

# remove nulls if possible
for i in range(len(yr)):
    if (len(datafullna[(datafullna['Year'] == yr[i]) & (datafullna['ArrDelay'].isnull())])/float(len(datafullna[datafullna['Year'] == yr[i]]))) * 100 > 3:
        print "may lose more than 3% data if nulls are removed."
    else:
        if i != 0: 
            datafull = pd.concat((datafull, datafullna[(datafullna['Year'] == yr[i]) & (datafullna['ArrDelay'].notnull())]), axis=0) 
        else:
            datafull = datafullna[(datafullna['Year'] == yr[i]) & (datafullna['ArrDelay'].notnull())]

# function to plot graphs consistently
def graphplt(dat, axis, ttle, lbl, lbls):
    dat.plot(ax=axis, title=ttle, marker='*', label=lbl).legend(labels=lbls, loc='center left', bbox_to_anchor=(1.02, 0.6)) 

def graphbar(dat, axis, ttle, lbl, lbls, coli):
    dat.plot(kind="bar", ax=axis, title=ttle, label=lbl, color=cm.Accent(float(coli)/5)).legend(labels=lbls, loc='center left', bbox_to_anchor=(1.02, 0.6))

# function to calculate the percentage delays
def percDelays(arr, onval, grpby):
    dfot = arr[onval <= 0].groupby(grpby).size().reset_index()
    dfot = dfot.rename(columns = {0: 'on-time_count'})
    dfdel = arr[onval > 0].groupby(grpby).size().reset_index()
    dfdel = dfdel.rename(columns = {0:'delayed_count'})
    #dfpd['delayed_count'] = dfdel['delayed_count']
    dfpd = dfot.merge(dfdel, how='outer') 
    dfpd['total_count'] = dfpd['on-time_count'] + dfpd['delayed_count']
    dfpd['perc_delayed'] = (dfpd['delayed_count'].astype('float64') / (dfpd['total_count'])) * 100
    
    return dfpd

print "Displaying time period graphs"
sys.stdout.flush()

# plot seperate graphs
# plot time/period based graph
fig, axes = plt.subplots(nrows=3, ncols = 2, figsize=(3,8))
for i in range(len(yr)):
    # split the data frame for each year 
    df1 = datafull[datafull['Year'] == yr[i]][['Year','Month','DayOfWeek','DayofMonth','ArrDelay']]
    #df1 = datafull[datafull['Year'] == yr[i]]

    # plot stats per year
    grphtitle = 'Delay view across months.'
    dfmonth = percDelays(df1, df1['ArrDelay'], df1.Month)
    dfmon = dfmonth[['Month','perc_delayed']]
    graphplt(dfmon.set_index('Month'), axes[0,1], grphtitle, yr[i], yr)
    grphtitle = 'Total flights\' count across months.'
    graphbar(dfmonth[['Month','total_count']].set_index('Month'), axes[0,0], grphtitle, yr[i], yr, i)

    grphtitle = 'Delay view across particular days of the week.'
    dfwk = percDelays(df1, df1['ArrDelay'], df1.DayOfWeek)
    dfwkf = dfwk.merge(daysdf, on='DayOfWeek', how='left')
    graphplt(dfwkf[['DayName','perc_delayed']].set_index('DayName'), axes[1,1], grphtitle, yr[i], yr)
    grphtitle = 'Total flights\' count across particular days of the week.'
    graphbar(dfwkf[['DayName','total_count']].set_index('DayName'), axes[1,0], grphtitle, yr[i], yr, i)

    grphtitle = 'Delay view across particular days of the month.'
    dfdmon = percDelays(df1, df1['ArrDelay'], df1.DayofMonth)
    graphplt(dfdmon[['DayofMonth','perc_delayed']].set_index('DayofMonth'), axes[2,1], grphtitle, yr[i], yr)
    grphtitle = 'Total flights\' across particular days of the month.'
    graphbar(dfdmon[['DayofMonth','total_count']].set_index('DayofMonth'), axes[2,0], grphtitle, yr[i], yr, i)
    
 
# setting the axis labels for timerange stats per year
for a in range(3):
    axes[a,1].set_xlabel('period')
    #axes[a,1].set_ylabel('average delay time')
    axes[a,1].set_ylabel('percentage delays')
plt.subplots_adjust(left=0.06,right=0.9,top=0.96,bottom=0.07,hspace=0.52,wspace=0.4)
plt.show()

print "Displaying percentage delay graphs for airports and carriers"
sys.stdout.flush()

# plot percentage graphs
fig, axes = plt.subplots(nrows=1, ncols = 2, figsize=(5,10))
for i in range(len(yr)):
    # split the data frame for each year
    df3 = datafull[datafull['Year'] == yr[i]][['Year','ArrDelay','UniqueCarrier','Description']]
    
    dfua = percDelays(df3, df3['ArrDelay'], ['UniqueCarrier','Description'])
    dfua = dfua[['UniqueCarrier','Description','total_count','perc_delayed']].sort(['perc_delayed'], ascending=False).head(10)
 
    grphtitle = 'Carriers with highest percentage delays.'
    graphplt(dfua[['UniqueCarrier','Description','perc_delayed']].set_index(['UniqueCarrier', 'Description']), axes[0], grphtitle, yr[i], yr) 
    grphtitle = 'Total count of flights for Carriers with highest percentage delays.'
    graphbar(dfua[['UniqueCarrier','Description','total_count']].set_index(['UniqueCarrier', 'Description']), axes[1], grphtitle, yr[i], yr, i)

plt.subplots_adjust(left=0.07,right=0.9,wspace=0.4,bottom=0.33)
for a in fig.axes:
    plt.sca(a)
    plt.xticks(rotation=45)
plt.show()

fig, axes = plt.subplots(nrows=1, ncols = 2, figsize=(5,10))
for i in range(len(yr)):
    # split the data frame for each year
    df3 = datafull[datafull['Year'] == yr[i]][['Year','ArrDelay','Dest', 'location']]

    dfda = percDelays(df3, df3['ArrDelay'], df3.Dest)
    dfda = dfda[['Dest','total_count','perc_delayed']].sort(['perc_delayed'], ascending=False).head(10)

    grphtitle = 'Airports with highest percentage delays.'
    graphplt(dfda[['Dest','perc_delayed']].set_index('Dest'), axes[1], grphtitle, yr[i], yr)
    grphtitle = 'Total flight count to Airports with highest percentage delays.'
    graphbar(dfda[['Dest','total_count']].set_index('Dest'), axes[0], grphtitle, yr[i], yr, i)

dfda = (dfda.merge(df3[['Dest','location']], on='Dest', how='left')).drop_duplicates()
print "Airport names and codes mapping: %s" % dfda[['Dest','location']]
sys.stdout.flush()
plt.subplots_adjust(left=0.07,right=0.9,wspace=0.4,bottom=0.33)
plt.show()

print "Displaying percentage delay graphs for origin airports and flight distance"
sys.stdout.flush()

fig, axes = plt.subplots(nrows=2, ncols = 2, figsize=(3,6))
for i in range(len(yr)):
    # split the dataframe for each year
    df4 = datafull[datafull['Year'] == yr[i]][['Year','ArrDelay','Origin','Distance']]

    print "calculating perc delay"
    sys.stdout.flush()
    dfoa = percDelays(df4, df4['ArrDelay'], df4.Origin)
    dfotp = dfoa.sort(['perc_delayed'], ascending=False).head(10)
    
    grphtitle = 'Origin airports with highest percentage delays.'
    graphplt(dfotp[['Origin','perc_delayed']].set_index('Origin'), axes[0,1], grphtitle, yr[i], yr)
    grphtitle = 'Total count of flights from airports with highest percentage delays.'
    graphbar(dfotp[['Origin','total_count']].set_index('Origin'), axes[0,0], grphtitle, yr[i], yr, i)

    dfdia = percDelays(df4, df4['ArrDelay'], df4.Distance)
    dfditp = dfdia.sort(['perc_delayed'], ascending=False).head(10)
    dfditp['Distance'] = dfditp['Distance'].apply(str)

    grphtitle = 'Distances covered with highest percentage delays.'
    graphplt(dfditp[['Distance','perc_delayed']].set_index('Distance'), axes[1,1], grphtitle, yr[i], yr)
    grphtitle = 'Distances covered with highest percentage delays.'
    graphbar(dfditp[['Distance','total_count']].set_index('Distance'), axes[1,0], grphtitle, yr[i], yr, i)

plt.subplots_adjust(top=0.94,bottom=0.14,left=0.07,right=0.9,hspace=0.85,wspace=0.5)
plt.show()

