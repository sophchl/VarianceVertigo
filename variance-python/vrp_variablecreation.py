# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 10:43:08 2020

@author: Sophia

input:
output:
    
"""

#%% setup

import numpy as np
import pandas as pd
import datetime as dt
import scipy.io as sio

#%% set variables

#%% import dates and try to handle them

dates = sio.loadmat('data/processed/ivs/_dates.mat')

# looks like that is a dictionary

for i in dates.keys():
    print(i)
    print('contains')
    print(dates[i])

# looks like what we need is in 'None'
print('type of None is', type(dates['None']))
print(dates['None'])

# or in '__function_workspace__' ?
print('type of __function_workspace__ is', type(dates['__function_workspace__']))
print(dates['__function_workspace__'])

pd.DataFrame(dates['__function_workspace__'])

#%% import data

# dates
dates = pd.read_csv('data/processed/ivs/dates.csv', header = None)
dates = dates.rename(columns={0:'dates'})
dates['dates'] = pd.to_datetime(dates['dates'])

# ivs
ivd = pd.read_csv("data/processed/ivs/IV_D_interpolated_030107_to_071015.csv", header = None)
ivu = pd.read_csv("data/processed/ivs/IV_U_interpolated_030107_to_071015.csv", header = None)

# we have to manually set headers becaut they are not contained in the csv files
ivd.columns = ['h1', 'h2', 'h3', 'h6', 'h9', 'h12']
ivu.columns = ['h1', 'h2', 'h3', 'h6', 'h9', 'h12']

ivu = ivu.sort_index()
ivd = ivd.sort_index()

# rv
rv = pd.read_csv("data/processed/rv/rv.csv", index_col = 0)
rv.index = pd.to_datetime(rv.index)

#%% add dates to ivs and put all dataframes to same length

# cut off dates where we don't have ivs computed
# from name of dataset, start: 03.01.2007, end: 07.10.2015

start = dt.datetime(2007,1,3)
end = dt.datetime(2015,10,7)

cut_dates = dates[(dates['dates'] >= start) & (dates['dates'] < end)]
ivd.index = cut_dates['dates']
ivu.index = cut_dates['dates']

cut_rv = rv[(rv.index >= start) & (rv.index < end)]

# we have to delete the first row of both ivs and rv
# return is nan in first row, hence overnight return set to -1, hence scaled variables really big
cut_rv = cut_rv.drop(dt.date(2007,1,3), axis = 0)
ivu = ivu.drop(dt.date(2007,1,3), axis = 0)
ivd = ivd.drop(dt.date(2007,1,3), axis = 0)

# compare dates of rv and ivu/ivd
missing_dates_rv = ivu.index[~ivu.index.isin(cut_rv.index)]
print(missing_dates_rv)

# interpolate the 15 missing days
add_to_rv = pd.DataFrame(np.nan, index = missing_dates_rv, columns = cut_rv.columns)
cut_rv = cut_rv.append(add_to_rv)
cut_rv = cut_rv.sort_index()
cut_rv = cut_rv.interpolate(method = 'linear')

# if both below are false, the indexes are the same
print('Any difference in indexes of ivs?', False in (ivu.index == ivd.index))
print('Any difference in index ov ivs and rv?', False in (ivu.index == cut_rv.index))

#%% In the following we need to sum rv over the past days to accumulate to heach h

# check if rolling windoes does what we want
# (this part of the code can be deleted after sb double checked)

h = 1
test1 = cut_rv['rv_u_sc'].rolling(window = 2).sum()
# for row i, this takes sum of i + i-1, but we want i-1 + i-2
test2 = test1.shift(periods = 1)
# this seems to work
test3 = cut_rv['rv_u_sc'].rolling(window = 10).sum()
test4 = test3.shift(periods = 1)
print(cut_rv['rv_u_sc'][0:30])
print(test4.iloc[0:30])

#%% create one dataframe per h

'''
for each maturity (h_month, h_month = 1,2,3,6,9,12) in month we create one dataset.
As we think they don't aggregate the actual calendaer month but for every day
the last days with the length of one month, we use 1 month = 21 trading days and
maturity (h_days, h_days = 21, 42, 63, 126, 189, 252) in days.

Per h we have a dataset with the following rows:
For each day i: from ivu, ivd row i, column h_month and from rv the sum of rows (i-h_days to i-1).
'''

tradingdays_month = 21
h_month = np.array([1,2,3,6,9,12])
h_days = h_month * tradingdays_month

list_dataframes = []

h = 1
df1 = pd.DataFrame(columns = ["rv", "rvu", "rvd", "ivu", "ivd"], index = cut_rv.index)
rvu_accum = cut_rv['rv_u_sc'].rolling(window = h_days[h-1]).sum()
df1["rvu"] = rvu_accum.shift(periods = 1)
rvd_accum =
df1["rvd"] = cut_rv['rv_d_sc']
df1["ivu"] = ivu.iloc[:,h-1]
df1["ivd"] = ivd.iloc[:,h-1]






    




