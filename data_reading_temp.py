# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 09:07:17 2020

@author: Sophia
"""

#%% load dependencies 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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


#%% process/add tbill (tb2)

tbill_raw2 = pd.read_csv('data/raw/tbill/rf3m.csv')
tb2 = tbill_raw2[:]

print(tb2.columns)
tb2.columns  = ['ident', 'date', 'bidytm', 'askytm', 'nomytm']
tb2['date'] = pd.to_datetime(tb2['date'])

tb2['rfm'] = ((1+(tb2.nomytm)/100)**(1/12))-1
tb2['rfy'] = tb2.nomytm/100

data_all = pd.merge(tb2[['date', 'rfm', 'rfy']], data_all, on = 'date')

#%% process/add tbill (tb3)

#tbill_raw3 = pd.read_csv('data/raw/3mtbill3.csv')
#tb3 = tbill_raw3[:]

#tb3.columns = ['date', 'rfm', 'level']
#tb3['date']= pd.to_datetime(tb3['date'], format='%Y%m%d')

#tb3['rfy'] = (1+tb3.rfm)**(12)-1

#data_all = pd.merge(tb3[['date', 'rfm', 'rfy']], data_all, on = 'date')

#%% process/add spx 

spx_raw = pd.read_csv('data/raw/spx/spx_monthly.csv')
spx = spx_raw[:]

spx.columns = ['date', 'vwred', 'vwrid', 'ewred', 'edrid', 'value', 'rtrnm']
spx['date'] = pd.to_datetime(spx['date'], format='%Y%m%d')

spx['rtrny'] = (1 + spx.rtrnm)**(12) - 1

for i in range(1,5):
    spx[('rtrnm_' + str(i))] = (spx.iloc[:,i] - spx.iloc[:,i].shift(1))/spx.iloc[:,i].shift(1)


data_all = pd.merge(spx[['date', 'rtrnm', 'rtrny', 'rtrnm_1', 'rtrnm_2', 'rtrnm_3', 'rtrnm_4']], data_all, on = 'date')

#%% work on whole dataset

# some attempts to get their numbers

# take difference of log return
data_all['excessya'] = 12*np.log(1 + data_all.rtrnm) - np.log(1 + data_all.rfy)

# difference of absolute return  log afterwards
data_all['excessyb'] = 12* np.log(1 + (data_all.rtrnm - data_all.rfm))

# same with annualized returns
data_all['excessyc'] = np.log(1 + data_all.rtrny) - np.log(1 + data_all.rfy)
data_all['excessyd'] = np.log(1 + (data_all.rtrny - data_all.rfy))

excess = data_all[['date', 'excessya', 'excessyb', 'excessyc', 'excessyd']]

# with the equiy/value weighted returns
#for i in range(1,5):
#    data_all[('excessya_' + str(i))] = 12*np.log(1 + data_all[('rtrnm_' + str(i))]) - np.log(1 + data_all.rfm)

data_rep = my_time_filter(excess, start_date, end_date)
print(data_rep.mean(axis = 0)*100)

data_precrisis = my_time_filter(excess, start_date, '2007-12-31')
print(data_precrisis.mean(axis = 0)*100)

#%% some plots

plt.plot(data_all.date, data_all.rtrnm)
plt.plot(data_all.date, data_all.rfm)
plt.title('monthly returns')
plt.show()

plt.plot(data_all.date, data_all.rtrny)
plt.plot(data_all.date, data_all.rfy)
plt.title('annualized monthly returns')