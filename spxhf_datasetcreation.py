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
import pandas_market_calendars as mcal

#%% set parameters

kappa = 0

#%% functions needed

def separate_tradingday_overnight(data):
    day = data[(data.index.time >= dt.time(9,30,0)) & 
               (data.index.time <= dt.time(16,0,0))]
    nightindex = data.index.difference(day.index)
    night = data.loc[nightindex,]
    return(day, night)


#%% loop over all files in directory to import the data from manual download
# directly aggregate to mide price in 5min during trading day
# do that only once!!

data_directory = "variance-python/data/raw/spxhf3"

list_dataframes = []

for file in os.listdir(data_directory):
    if file.endswith('.csv'):
        filename = data_directory + "/" + file
        df = pd.read_csv(filename, )
        df.index = pd.to_datetime(df['DATE'].astype(str) + ":" + df['TIME'], format = '%Y%m%d:%H:%M:%S')
        df['mid'] = (df['BID'] + df['OFR'])/2
        df = df.drop(['BID', 'OFR', 'DATE', 'TIME', 'SYMBOL'], axis = 1)
        df = df.resample('5T').median()
        df = separate_tradingday_overnight(df)[0]
        list_dataframes.append(df)
        print(file)
        continue
    else:
        continue
    
#%% create one big dataframe, sort by date and time, separate day and night
# do that only once

spx1 = pd.concat(list_dataframes)
spx1 = spx1.sort_index()
spx1.to_csv("variance-python/data/raw/spxhf4/5minspx2007.csv")

#%% import data from 2007

spx1 = pd.read_csv("variance-python/data/raw/spxhf4/5minspx2007.csv", index_col = 0)
spx1.index = pd.to_datetime(spx1.index)
 
#%% import the data 2008 - 2020

spx2 = pd.read_csv("variance-python/data/raw/spxhf2/SPY/SPY.csv", index_col = 0)
spx2.index = pd.to_datetime(spx2.index)
spx2['mid'] = (spx2.open + spx2.close)/2
spx2 = spx2.resample('5T').median()
spx2 = spx2.drop(['open', 'close'], axis = 1)
spx2 = separate_tradingday_overnight(spx2)[0]

#%% join data 2007 - 2020 and save them

spx = pd.concat([spx2, spx1])
spx = spx.sort_index()
spx1 = spx1[spx1.index.year < 2008]

spx = pd.concat([spx1, spx2])

print('Are there overlaps?', True in spx.index.duplicated(keep = "first"))

spx.to_csv("variance-python/data/raw/spxhf4/5minspx20072.csv")

#%% import dataset 2007 - 2020

spx = pd.read_csv("variance-python/data/raw/spxhf4/5minspx20072.csv", index_col = 0)
spx.index = pd.to_datetime(spx.index)

#%% check for missing values

print('length of dataset initial:', len(spx))
missing_days = pd.date_range(start = dt.date(2008,1,2), end = dt.date(2020,4,9)).difference(spx.index.date)
print('number of missing days:', len(missing_days))
print('number of Nans:', spx.isnull().sum())

# remove weekends 
spx = spx[spx.index.dayofweek < 5]
print('length of dataset without weekend:', len(spx))
print('number of Nans:', spx.isnull().sum())

# remove non-trading days
nyse = mcal.get_calendar('NYSE')
early = nyse.schedule(start_date=spx.index.date[1], end_date=spx.index.date[-1])
no_trading_days = np.setdiff1d(list(spx.index.date),list(early.index.date))

spx['to_drop'] = [1 if x in no_trading_days else 0 for x in spx.index.date]
index_to_drop = spx[spx['to_drop'] == 1].index
spx = spx.drop(index = index_to_drop, columns = ['to_drop'])

print('length of dataset witout holiday days:', len(spx))
print('number of Nans:', spx.isnull().sum())
spx.isnull().values.any()
spx[spx.isna().any(axis=1)]

#%% save cleanest version of dataset 2007 - 2020

spx.to_csv("variance-python/data/raw/spxhf4/5minspx20073.csv")

