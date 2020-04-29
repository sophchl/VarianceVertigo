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


#%% create one dataframe per h

'''
for each maturity (h_month, h_month = 1,2,3,6,9,12) in month we create one dataset.
As we think they don't aggregate the actual calendaer month but for every day
the last days with the length of one month, we use 1 month = 21 trading days and
maturity (h_days, h_days = 21, 42, 63, 126, 189, 252) in days.

Per h we have a dataset with the following rows:
For each day i: from ivu, ivd row i, column h_month and from rv the sum of rows (i-h_days to i-1).
'''

print(ivd.index)
print(cut_rv.index)

tradingdays_month = 21
h_month = np.array([1,2,3,6,9,12])
h_days = h_month * tradingdays_month

list_dataframes = []


df1 = pd.DataFrame(columns = ["date", "rv", "rvu", "rvd", "ivu", "ivd"])
df1["date"]







    




