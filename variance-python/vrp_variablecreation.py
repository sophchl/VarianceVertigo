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

#%% import data

# dates
dates = pd.read_csv('data/processed/ivs/dates.csv', header = None)
dates = dates.rename(columns={0:'dates'})
dates['dates'] = pd.to_datetime(dates['dates'])

# ivs
ivd = pd.read_csv("data/processed/ivs/IV_D_030100_to_291217.csv", index_col = 6)
ivu = pd.read_csv("data/processed/ivs/IV_U_030100_to_291217.csv", index_col = 6) 
ivd.index = pd.to_datetime(ivd.index)
ivu.index = pd.to_datetime(ivu.index)

# rv
rv = pd.read_csv("data/processed/rv/rv.csv", index_col = 0)
rv.index = pd.to_datetime(rv.index)

#%% set the right timeframe where data overlap

# cut off dates of rv where we don't have ivs computed
start_date_iv = ivu.index[0]
end_date_iv = ivu.index[-1]
cut_rv = rv[(rv.index >= start_date_iv) & (rv.index <= end_date_iv)]

start_date_rv = rv.index[0]
end_date_rv = rv.index[-1]
cut_ivu = ivu[(ivu.index >= start_date_rv) & (ivu.index <= end_date_rv)]
cut_ivd = ivd[(ivd.index >= start_date_rv) & (ivd.index <= end_date_rv)]

# interpolate dates in rv that are missing
missing_dates_rv = cut_ivu.index[~cut_ivu.index.isin(cut_rv.index)]
print('interpolate days:', len(missing_dates_rv))
add_to_rv = pd.DataFrame(np.nan, index = missing_dates_rv, columns = cut_rv.columns)
cut_rv = cut_rv.append(add_to_rv)
cut_rv = cut_rv.sort_index()
cut_rv = cut_rv.interpolate(method = 'linear')

# if both below are false, the indexes are the same
print('Any difference in indexes of ivs?', False in (cut_ivu.index == cut_ivd.index))
print('Any difference in index ov ivs and rv?', False in (cut_ivu.index == cut_rv.index))

# compare dates of rv and ivu/ivd
missing_dates_rv = cut_ivu.index[~cut_ivu.index.isin(cut_rv.index)]
print('Days that are in iv but not in rv:', missing_dates_rv)

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
dict_dataframes = {}

for i in range(0,len(h_days)):
    df = pd.DataFrame(columns = ["rvu", "rvd", "ivu", "ivd"]) 
    rvu_accum = cut_rv['rv_u_sc'].rolling(window = h_days[i]).sum()
    df["rvu"] = rvu_accum.shift(periods = 1)
    rvd_accum = cut_rv['rv_d_sc'].rolling(window = h_days[i]).sum()
    df["rvd"] = cut_rv['rv_d_sc']
    df["ivu"] = cut_ivu.iloc[:,i]
    df["ivd"] = cut_ivd.iloc[:,i]
    dict_dataframes[h_month[i]] = df
    list_dataframes.append(df)

#%% calculate VRP

for df in list_dataframes:
    df['vrpu'] = df['ivu'] - df['rvu']
    df['vrpd'] = df['ivd'] - df['rvd']
    df['vrp'] = df['vrpu'] + df['vrpd']
    

#%% add the excess returns








    




