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


#%% lopp over all files in directory to import the data

data_directory = "data/raw/spxhf"

list_dataframes = []

for file in os.listdir(data_directory):
    if file.endswith('.csv'):
        filename = data_directory + "/" + file
        df = pd.read_csv(filename, )
        list_dataframes.append(df)
        continue
    else:
        continue
    
#%% create one big dataframe, sort by date and time

spx = pd.concat(list_dataframes)
spx.columns = ['symbol', 'date', 'time', 'bid']
spx = spx.drop(['symbol'], axis = 1)
spx_datetime = spx['date'].astype(str) + ":" + spx['time']
spx.index = pd.to_datetime(spx_datetime, format = '%Y%m%d:%H:%M:%S')
spx['date'] = pd.to_datetime(spx['date'], format='%Y%m%d').dt.date
spx['time'] = pd.to_datetime(spx['time'], format='%H:%M:%S').dt.time

spx = spx.sort_index()

# check for doublicates and missings: not done yet

#%% take only 5-min returns

# A: selecting values 

spx1 = spx.resample('1T').mean()
fivemin = np.arange(dt.datetime(1996,9,30), dt.datetime(1999,12,2), dt.timedelta(minutes = 5)).astype(dt.datetime)
fivemin = pd.DataFrame(fivemin)
fivemin.index = fivemin.iloc[:,0]

spx5a = pd.merge(spx1, fivemin, how = 'right', right_index = True, left_index = True)
spx5a = spx5a.drop([0], axis = 1)

# B: 5 min resample

spx5b = spx.resample('5T').mean()

# see if it does what we want (because many Nan)
spx.iloc[1:20,]
spx5b.iloc[1:10,]
spx.iloc[2:12,].mean()
# looks as average of e.g. 8:30 are all values from 8:25 to 8:30 etc.

#%% split in daily and overnight

# what is the latest and earliest time we have per day?

# definitely not the fastest and most precise way but 
# for the first 1,000 obverstavion we always have times between 08:59:51 and 18:30:04
for day in spx.iloc[1:10000,].groupby("date"):
    print(min(spx['time']), max(spx['time']))




#%% average bid ask quotes

#spx['level'] = np.mean(spx['bid'], spx['offer'])

#%% calculate upside and downside realized variance

#%% calculate total realized variance: 2 ways

#%% apply scaling

#%% accumulating