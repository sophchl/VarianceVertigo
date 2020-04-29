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

kappa = 0

#%% import data

spx = pd.read_csv("variance-python/data/raw/spxhf4/5minspx20074.csv", index_col = 0)
spx.index = pd.to_datetime(spx.index)

#%% calculate return and realized variances

spx['rtrn'] = np.log(spx.mid) - np.log(spx.mid.shift(1))

# create mydata2: aggregate to rv daily data
spx_daily = (spx[['rtrn']]**2).resample('1D').sum()
spx_daily.columns = ['rv']

# add squared overnight return (have to do resample sum to get to daily data, but sum of only one value)
spx_daily['open'] = spx[spx.index.time == dt.time(9,30,0)].mid.resample('1D').sum()
spx_daily['close'] = spx[spx.index.time == dt.time(16,0,0)].mid.resample('1D').sum()
spx_daily['overnight'] = np.log(spx_daily['open']) - np.log(spx_daily['close'].shift(1))
spx_daily['rv2'] = spx_daily['rv'] + spx_daily['overnight']**2

# 732 Nan rows out of 4482 

#%% calculate upside and downside realized variance

spx_daily['rv_u'] = (spx[spx['rtrn'] > kappa]['rtrn']**2).resample('1D').sum()
spx_daily['rv_d'] = (spx[spx['rtrn'] <= kappa]['rtrn']**2).resample('1D').sum()

# test if up ad down rv sums to rv (if result is False we are good)
print("Does sum of rv up and down deviate from rv?", False in round((spx_daily['rv_u'] + spx_daily['rv_d']),10) == round(spx_daily['rv'],10))

# add overnight 
spx_daily['rv_u2'] = spx_daily['rv_u'] + spx_daily[spx_daily['overnight'] > kappa]['overnight']**2
spx_daily['rv_d2'] = spx_daily['rv_d'] + spx_daily[spx_daily['overnight'] <= kappa]['overnight']**2

spx_daily = spx_daily.drop(['close', 'open', 'overnight'], axis = 1)

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

