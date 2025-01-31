# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 10:43:08 2020

@author: Sophia

input: implied volatility, realized volatility and excess returns as single datasets (from processed)
output: one dataset per aggregation level h
    
"""

#%% load dependencies

import numpy as np
import pandas as pd
import pandas_market_calendars as mcal

#%% define functions

def my_time_filter(df,start,end):
    cut_df = df[(df.index >= start) & (df.index <= end)]
    return cut_df

def check_for_nans(data):
    # does nan check
    rows_w_nans = data[data.isnull().any(axis = 1)]
    number_nans = len(rows_w_nans)
    print('number of nans is:', number_nans, ' \n rows with nans are: \n', rows_w_nans)
   

#%% import data

# ivs
ivu = pd.read_csv("data/processed/ivs/IV_U_030100_to_291217.csv", index_col = 6) 
ivu.index = pd.to_datetime(ivu.index)
ivd = pd.read_csv("data/processed/ivs/IV_D_030100_to_291217.csv", index_col = 6)
ivd.index = pd.to_datetime(ivd.index)

# rv
rv = pd.read_csv("data/processed/rv/rv.csv", index_col = 0)
rv.index = pd.to_datetime(rv.index)

# excessreturn
excess = pd.read_csv("data/processed/excessreturn/excessreturn_daily.csv", index_col = 0)
excess.index = pd.to_datetime(excess.index)

#%% set the right timeframe where data overlap

# 1st: cut our data to the same start end end
common_index = ivu.index.intersection(rv.index)
common_index = common_index.intersection(excess.index)
start = common_index[0]
end = common_index[-1]

cut_ivu = my_time_filter(ivu, start, end)
cut_ivd = my_time_filter(ivd, start, end)
cut_rv = my_time_filter(rv, start, end)
cut_excess = my_time_filter(excess, start, end)

# 2nd: make ure the days in between start and end are the same

# find all trading days in the period where our data overlaps
nyse = mcal.get_calendar('NYSE')
early = nyse.schedule(start_date = start, end_date = end)

# summarize our data availability
print('iv ranges from', ivu.index[0], 'to', ivu.index[-1], 'number of days is:', len(ivu.index), '.\n'
      'rv ranges from', rv.index[0], 'to', rv.index[-1], 'number of days is:', len(rv.index), '.\n'
      'rtrn range from', excess.index[0], 'to', excess.index[-1], 'number of days is:', len(excess.index), '.\n'
      'their common date range is', start, 'to', end, 'number of trading days in that range is:', len(early.index), '.\n'
      'the cut dataframes have number of days: iv:', len(cut_ivu.index), ', rv:', len(cut_rv.index), ', excess:', len(cut_excess.index), '.')

# check for nans (none present)
check_for_nans(cut_ivu)
check_for_nans(cut_rv)
check_for_nans(cut_excess)

# interpolate dates in rv that are missing
missing_dates_rv = cut_ivu.index[~cut_ivu.index.isin(cut_rv.index)]
print('interpolate days in rv:', len(missing_dates_rv))
add_to_rv = pd.DataFrame(np.nan, index = missing_dates_rv, columns = cut_rv.columns)
cut_rv = cut_rv.append(add_to_rv)
cut_rv = cut_rv.sort_index()
cut_rv = cut_rv.interpolate(method = 'linear')

# interpolate dates in excess returns that are missing
missing_dates_excess = cut_ivu.index[~cut_ivu.index.isin(cut_excess.index)]
print('interpolate days in rtrn:', len(missing_dates_excess))
add_to_excess = pd.DataFrame(np.nan, index = missing_dates_excess, columns = cut_excess.columns)
cut_excess = cut_excess.append(add_to_excess)
cut_excess = cut_excess.sort_index()
cut_excess = cut_excess.interpolate(method = 'linear')

# if both below are false, the indexes are the same
print('Any difference in indexes of ivs?', False in (cut_ivu.index == cut_ivd.index))
print('Any difference in index ov ivs and rv?', False in (cut_ivu.index == cut_rv.index))
print('Any difference in index ov ivs and excess?', False in (cut_ivu.index == cut_excess.index))

# compare dates of rv and ivu/ivd
missing_dates_rv = cut_ivu.index[~cut_ivu.index.isin(cut_rv.index)]
print('Days that are in iv but not in rv:', missing_dates_rv)


#%% In the following we need to sum rv over the past days to accumulate to heach h

# check if rolling windoes does what we want
# (this part of the code can be deleted after sb double checked)

test1 = cut_rv['rv_u_sc'].rolling(window = 5).sum()
print(cut_rv['rv_u_sc'][0] + cut_rv['rv_u_sc'][1])

# this takes the sum of row i-4 to i
# the paper says, expected value under P of RV is RV_t-h,h,
# which is by definition the sum of RV_t-h+1 = RV_t-(h-1) to RV_t.
# so we need to take the window as h


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
    df["rvu"] = rvu_accum
    rvd_accum = cut_rv['rv_d_sc'].rolling(window = h_days[i]).sum()
    df["rvd"] = rvd_accum
    df["ivu"] = cut_ivu.iloc[:,i]
    df["ivd"] = cut_ivd.iloc[:,i]
    dict_dataframes[h_month[i]] = df
    list_dataframes.append(df)

#%% calculate VRP

for df in list_dataframes:
    df['vrpu'] = df['ivu'] - df['rvu']
    df['vrpd'] = df['ivd'] - df['rvd']
    df['vrp'] = df['vrpu'] + df['vrpd']
    
#%% check for nans

for df in list_dataframes:
    check_for_nans(df)
    
#%% save datasets

names_dataframes = ['h01', 'h02', 'h03', 'h06', 'h09', 'h12']

for i in range(0,len(list_dataframes)):
    list_dataframes[i].to_csv('data/processed/vrp/' + names_dataframes[i] + '.csv')

    








    




