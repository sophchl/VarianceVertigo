# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 11:32:13 2020

@author: Sophia
"""

#%% setup

import os
import numpy as np
import pandas as pd
import datetime as dt

#%% functions needed

def separate_tradingday_overnight(data):
    day = data[(data.index.time > dt.time(9,30,0)) & 
               (data.index.time < dt.time(16,0,0))]
    nightindex = data.index.difference(day.index)
    night = data.loc[nightindex,]
    return(day, night)


#%% lopp over all files in directory to import the data

data_directory = "variance-python/data/raw/spxhf"

list_dataframes = []

for file in os.listdir(data_directory):
    if file.endswith('.csv'):
        filename = data_directory + "/" + file
        df = pd.read_csv(filename, )
        list_dataframes.append(df)
        continue
    else:
        continue
    
#%% create one big dataframe, sort by date and time, separate day and night

spx = pd.concat(list_dataframes)
spx.columns = ['symbol', 'date', 'time', 'bid']
spx = spx.drop(['symbol'], axis = 1)
spx.index = pd.to_datetime(spx['date'].astype(str) + ":" + spx['time'], format = '%Y%m%d:%H:%M:%S')
spx['date'] = pd.to_datetime(spx['date'], format='%Y%m%d').dt.date
spx['time'] = pd.to_datetime(spx['time'], format='%H:%M:%S').dt.time

spx = spx.sort_index()

# check for doublicates and missings: not done yet

day, night = separate_tradingday_overnight(spx)

#%% take only 5-min prices

# A: selecting values 

day1 = day.resample('1T').mean()
fivemin = np.arange(dt.datetime(1996,9,30), dt.datetime(1999,12,2),
                          dt.timedelta(minutes = 5)).astype(dt.datetime)
fivemin = pd.DataFrame(index = fivemin)
fivemin_day = separate_tradingday_overnight(fivemin)[0]

spx5a = pd.merge(day1, fivemin_day, right_index = True, left_index = True)

# B: 5 min resample
# looks like average of e.g. 8:30 are all values from 8:25 to 8:30 etc.

spx5b = day.resample('5T').mean()
spx5b =  spx5b[1:]

# continue with one of them

mydata = spx5b

#%% average bid ask quotes

#spx['level'] = np.mean(spx['bid'], spx['offer'])

#%% calculate return and realized variances

mydata['return'] = (mydata.bid - mydata.bid.shift(1))/(mydata.bid)

# create mydata2: aggregate to daily data
mydata2 = (mydata[['return']].groupby(mydata.index.date).sum())**2
mydata2.columns = ['rv']

# add squared overnight return
spx1 = spx.resample('1T').mean()
mydata2['open'] = spx1[spx1.index.time == dt.time(9,31,0)].bid.resample('1D').sum()
mydata2['close'] = spx1[spx1.index.time == dt.time(16,0,0)].bid.resample('1D').sum()
mydata2['overnight'] = (mydata2['open'] - mydata2['close'])/mydata2['close']
mydata2['rv2'] = mydata2['rv'] + mydata2['overnight']**2

# overnight return is huge compared to 5-min variances!!


#%% calculate upside and downside realized variance



#%% apply scaling

#%% accumulating

#%% dropped

# what is the latest and earliest time we have per day? 08:59:51 - 18:30:04 (first 1,0000)
# not very neat though

def get_fl_time(data, length):
    for day in data.iloc[1:length,].groupby(data.iloc[1:length,].index.date):
        print(min(data.index.time), max(data.index.time))
        
get_fl_time(day, 500)

