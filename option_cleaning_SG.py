# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 19:26:44 2020

@author: Sophia
"""

## 1. datetime
# I think it would help from the start, to turn our dataset into a timeseries, hence make the timestamp the index
options.index = 

## 1. days with less that 2 OTM calls and puts 
# tradeoff with loops: easy to make sure they do what we want to, but I think they are computationally expensive

# get all trading days
all_tradingdays = as.list(options.index.dt.date.unique())

# find all arbitrage days (less than 2 otm calls and puts)
# create a True/False variable for otm
options['otm'] = ((options['cp_flag'] == 'C') & (options['moneyness']>1)) | (
    (options['cp_flag'] == 'P') & (options['moneyness']<1))
# count how many OTM calls and puts per day
callotm = options[options['otm'] == True & options['cp_flag'] == 'C'].resample('1D').count()
putotm = options[options['otm'] == True & options['cp_flag'] == 'P'].resample('1D').count()

# dates with less than 2 OTM calls or 2 OTM puts
options.drop([callotm[callotm['score'] < 2].index] + [putotm[putotm['score'] < 2].index])

