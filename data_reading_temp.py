# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 09:07:17 2020

@author: Sophia
"""

#%% load dependencies 

import numpy as np
import pandas as pd
#from datetime import datetime

#%% global variables

data_all = pd.DataFrame()
data_all['date'] = pd.date_range('1996-01-01', '2020-03-31', freq = 'M').tolist()

start_date = '1996-09-30'
end_date = '2015-03-31'

def my_time_filter(df, start_date, end_date):
    
    after_start_date = df['date'] >= start_date
    before_end_date = df['date'] <= end_date
    between_dates = after_start_date & before_end_date
    filtered_df = df[between_dates]
    return(filtered_df)

#%% read tbill

tbill_raw1 = pd.read_csv('data/raw/3mtbill1.csv')
tb1 = tbill_raw1[:]

tbill_raw2 = pd.read_csv('data/raw/3mtbill2.csv')
tb2 = tbill_raw2[:]

#%% process/add tbill (tb1)

print(tb1.columns)
tb1['KYCRSPID']
tb1['TDATDT']
tb1['TMATDT']
tb1['TBANKDT']

#%% process/add tbill (tb2)

print(tb2.columns)
tb2.columns  = ['ident', 'date', 'bidytm', 'askytm', 'nomytm']
tb2['date'] = pd.to_datetime(tb2['date'])

tb2['rf'] = ((1+(tb2['nomytm'])/100)**(1/12))-1
tb2['rfy'] = tb2['nomytm']/100

data_all = pd.merge(tb2[['date', 'rf', 'rfy']], data_all, on = 'date')

#%% read spx

spx_raw = pd.read_csv('data/raw/spx.csv')
spx = spx_raw[:]

#%% process/add spx 

spx.columns = ['date', 'value', 'count', 'level', 'return']
spx['date'] = pd.to_datetime(spx['date'], format='%Y%m%d')

spx['logrtn'] = np.log(spx.level) - np.log(spx.level.shift(1))
spx['logrtny'] = spx['logrtn']*12

data_all = pd.merge(spx[['date', 'logrtn', 'logrtny']], data_all, on = 'date')

#%% read options

#spxoptions = pd.read_csv('data/raw/optionspx.csv')
#optionwork = spxoptions

#%% process/add options

#%% work on whole dataset

data_all['excessm'] = data_all['logrtn'] - data_all['rf']
data_all['excessy'] = data_all['logrtny'] - data_all['rfy']

data_rep = my_time_filter(data_all, start_date, end_date)
print(data_rep.mean()*100)
print(data_rep)

#%% sorted

# 