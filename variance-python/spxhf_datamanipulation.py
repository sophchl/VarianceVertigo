# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:53:09 2020

@author: Sophia

input: spy 5min data
output: RV upside and downside, daily frequency

"""

#%% setup

import numpy as np
import pandas as pd
import datetime as dt
from matplotlib import pyplot

#%% set variables

kappa = 0

#%% functions needed

def check_for_nans(data):
    # does nan check
    rows_w_nans = data[data.isnull().any(axis = 1)]
    number_nans = len(rows_w_nans)
    print('number of nans is:', number_nans, ' \n rows with nans are: \n', rows_w_nans)
    
def add_overnight_up(data, kappa, filler):
    # if overnigth return larger kappa, add it to rv_u, else leave rv_u as is
    if data['overnight'] > kappa:
        val = data['rv_u'] + data['overnight']**2
    elif data['overnight'] <= kappa:
        val = data['rv_u']
    else:
        val = -1
    return val

def add_overnight_down(data, kappa, filler):
    # if overnigth return smaller/equal kappa, add it to rv_d, else leave rv_d as is
    if data['overnight'] <= kappa:
        val = data['rv_d'] + data['overnight']**2
    elif data['overnight'] > kappa:
        val = data['rv_d']
    else:
        val = -1
    return val

#%% import data

spx = pd.read_csv("data/processed/spxhf/spx5min.csv", index_col = 0)
spx.index = pd.to_datetime(spx.index)

oxford_data = pd.read_csv("data/processed/oxford5min/oxfordmanrealizedvolatilityindices.csv", )
oxford_data['date'] = oxford_data.iloc[:,0].str.slice(0,10,1)
oxford_data.index = pd.to_datetime(oxford_data.date)

#%% calculate return and realized variances

spx['rtrn'] = np.log(spx.mid) - np.log(spx.mid.shift(1))

check_for_nans(spx)

# aggregate to rv daily data (rv = sum of squared returns)
spx_daily = (spx[['rtrn']]**2).resample('1D').sum()
spx_daily.columns = ['rv']

# delete days that were not in dataset before (probably weekend and holiday, see checks in "spxhf_datasetcreation") 
spx_daily = spx_daily[spx_daily.index.isin(spx.index.date)]

print('same number of days in spx and spx_daily?', len(np.unique(spx[['date']])) == len(spx_daily))

check_for_nans(spx_daily)

# add squared overnight return (have to do resample.sum to get to daily data, but sum of only one value)
spx_daily['open'] = spx[spx.index.time == dt.time(9,30,0)].mid.resample('1D').sum()
spx_daily['close'] = spx[spx.index.time == dt.time(16,0,0)].mid.resample('1D').sum()
spx_daily['overnight'] = np.log(spx_daily['open']) - np.log(spx_daily['close'].shift(1))
spx_daily['rv2'] = spx_daily['rv'] + spx_daily['overnight']**2

check_for_nans(spx_daily)

# how many days and Nans?
print('spx 5min data contains', len(np.unique(spx[['date']])), 'days. The daily data contains ',
      len(spx_daily), 'days, and ',len(spx_daily[spx_daily.isnull().any(axis=1)]), 'NaNs.')

# compare to oxford rv
oxford_data = oxford_data[oxford_data.Symbol == '.SPX']
oxford_data = oxford_data[['rv5', 'open_price', 'close_price']]
oxford_data = oxford_data[oxford_data.index.year >= 2008]

oxford_data.rv5.plot()
spx_daily.rv.plot()

# our data is slightly off but hard to see

#%% calculate upside and downside realized variance

spx_daily['rv_u'] = (spx[spx['rtrn'] > kappa]['rtrn']**2).resample('1D').sum()
spx_daily['rv_d'] = (spx[spx['rtrn'] <= kappa]['rtrn']**2).resample('1D').sum()

check_for_nans(spx_daily)

# test if up ad down rv sums to rv (if result is False we are good)
print("Does sum of rv up and down deviate from rv?", False in round((spx_daily['rv_u'] + spx_daily['rv_d']),10) == round(spx_daily['rv'],10))
        
# add overnight 
spx_daily['rv_u2'] = spx_daily.apply(add_overnight_up, args = (kappa, 0), axis=1)
spx_daily['rv_d2'] = spx_daily.apply(add_overnight_down, args = (kappa, 0), axis=1)

# manual check (looks ok, what do you think?)
spx_daily[['rv_d', 'rv_u', 'overnight', 'rv_d2', 'rv_u2']]

# remove variables we don't need
spx_daily = spx_daily.drop(['close', 'open', 'overnight'], axis = 1)

check_for_nans(spx_daily)

#%% apply scaling (silvias code, my data2 is what I named spx_daily)

'''
sample_var= np.var(mydata2['rv_tot'])
mydata2['rv_scaled']= mydata2['rv_tot']/sample_var
sample_avg=np.mean(mydata2['rv_scaled'])

mydata2['rv_U_scaled']=(mydata2['rv_U_tot'] * sample_var) / (sample_avg)
mydata2['rv_D_scaled']=(mydata2['rv_D_tot'] * sample_var) / (sample_avg)
mydata2['rv_scaled']=mydata2['rv_U_scaled']+mydata2['rv_D_scaled']
mydata2['date'] = mydata2.index
mydata2['month'] = pd.to_datetime(mydata2['date'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m'))

'''
#%% apply scaling, my code 

sample_var_returns = np.var(spx.rtrn) # modification: variance of returns, not rv or?
sample_avg_rv = np.mean(spx_daily['rv2']) # modification: average of unscaled rv or?

spx_daily['rv_scaled']= spx_daily['rv2']/sample_var_returns
spx_daily['rv_u_scaled']=(spx_daily['rv_u2'] * sample_var_returns) / (sample_avg_rv)
spx_daily['rv_d_scaled']=(spx_daily['rv_d2'] * sample_var_returns) / (sample_avg_rv)

spx_need = spx_daily[['rv2', 'rv_u2', 'rv_d2', 'rv_scaled', 'rv_u_scaled', 'rv_d_scaled']]
spx_need.columns = ['rv', 'rv_u', 'rv_d', 'rv_sc', 'rv_u_sc', 'rv_d_sc']

check_for_nans(spx_need)

#%% export the data

spx_need.to_csv("data/processed/rv/rv.csv")
