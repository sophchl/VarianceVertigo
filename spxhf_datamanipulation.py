# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:53:09 2020

@author: Sophia
"""

#%% setup

import os
import numpy as np
import pandas as pd
import datetime as dt

#%% import data

mydata = pd.read_csv("variance-python/data/raw/spxhf4/5minspx20073.csv",)

#%% calculate return and realized variances

mydata['rtrn'] = np.log(mydata.bid) - np.log(mydata.bid.shift(1))

# create mydata2: aggregate to rv daily data
mydata2 = (mydata[['rtrn']]**2).resample('1D').sum()
mydata2.columns = ['rv']

# add squared overnight return
spx1 = spx.resample('1T').mean()
mydata2['open'] = spx1[spx1.index.time == dt.time(9,31,0)].bid.resample('1D').mean()
mydata2['close'] = spx1[spx1.index.time == dt.time(16,0,0)].bid.resample('1D').mean()
mydata2['overnight'] = np.log(mydata2['open']) - np.log(mydata2['close'].shift(1))
mydata2['rv2'] = mydata2['rv'] + mydata2['overnight']**2

#%% calculate upside and downside realized variance

mydata2['rv_u'] = (mydata[mydata['rtrn'] > kappa]['rtrn']**2).resample('1D').sum()
mydata2['rv_d'] = (mydata[mydata['rtrn'] <= kappa]['rtrn']**2).resample('1D').sum()

# test
print(False in round((mydata2['rv_u'] + mydata2['rv_d']),10) == round(mydata2['rv'],10))

# add overnight 
mydata2['rv_u2'] = mydata2['rv_u'] + mydata2[mydata2['overnight'] > kappa]['overnight']**2
mydata2['rv_d2'] = mydata2['rv_d'] + mydata2[mydata2['overnight'] <= kappa]['overnight']**2

mydata2 = mydata2.drop(['close', 'open', 'overnight'], axis = 1)

#%% apply scaling

#%% accumulating

#%% dropped

# what is the latest and earliest time we have per day? 08:59:51 - 18:30:04 (first 1,0000)
# not very neat though

def get_fl_time(data, length):
    for day in data.iloc[1:length,].groupby(data.iloc[1:length,].index.date):
        print(min(data.index.time), max(data.index.time))
        
get_fl_time(day, 500)

#(mydata[['rtrn']]**2).groupby(mydata.index.date).sum()

# separate day and night

