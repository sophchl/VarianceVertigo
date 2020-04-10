# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 19:26:44 2020

@author: Sophia
"""

#%% setup

import os
import pandas as pd
import numpy as np
import datetime as dt

#%% read dataset

options = pd.read_csv('option-first-2-month.csv')

#%% fist look at datset

print(options.columns)

#%%comments

## 1 datetime index
# I think it can help to make the timestamp our index
options.index = pd.to_datetime(options.date, format = "%Y%m%d").dt.date


## 2 datasets
# qrobably a question of style, but I usually keep a "raw" dataset, 
# and instead of dropping the variables I don't need I add those that I do need
# to a new dataset, that I will use at the end. Like that we can always go back 
# to the raw dataset anytime in the code if we need sth.
options_clean = pd.DataFrame(index = options.index)

# .. no comments in between just need to copy&paste some code
options['strike_price'] = options['strike_price']/1000
options['moneyness'] = options['strike_price']/options['forward_price']

## 3 days with less that 2 OTM calls and puts 
# tradeoff with loops: easy to make sure they do what we want to, but expensive

# get all trading days
all_tradingdays = options.index.unique()

# find all arbitrage days (less than 2 otm calls and 2 otm puts)
# create a True/False variable for otm
options['otm'] = ((options['cp_flag'] == 'C') & (options['moneyness']>1)) | (
    (options['cp_flag'] == 'P') & (options['moneyness']<1))
# count how many OTM calls and puts per day
callotm = options[(options.otm == True) & (options.cp_flag == 'C')].otm.groupby(
    options[(options.otm == True) & (options.cp_flag == 'C')].index).count()
putotm = options[(options.otm == True) & (options.cp_flag == 'P')].otm.groupby(
    options[(options.otm == True) & (options.cp_flag == 'P')].index).count()

# if we want to delete dates wich don't have either or
options = options.drop(callotm[callotm['otm'] < 2].index, axis = 0)
options = options.drop(putotm[putotm['otm'] < 2].index, axis = 0)
# if we want to delete dates don't have both
options = options.drop(callotm[callotm < 2].index.intersection(putotm[putotm < 2].index))

del callotm, putotm

