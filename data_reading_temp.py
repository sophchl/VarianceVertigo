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
data_all['date'] = pd.date_range('1996-01-01', '2020-03-31', freq = 'D').tolist()

start_date = '1996-09-30'
end_date = '2015-03-31'

def my_time_filter(df, start_date, end_date):
    
    after_start_date = df['date'] >= start_date
    before_end_date = df['date'] <= end_date
    between_dates = after_start_date & before_end_date
    filtered_df = df[between_dates]
    return(filtered_df)


#%% process/add tbill (tb)

tb = pd.read_csv('variance-python/data/raw/tbill/rf3m2.csv')

print(tb.columns)
tb.columns  = ['ident', 'date', 'bidytm', 'askytm']
tb['avba'] = (tb.bidytm + tb.askytm)/2
tb['date'] = pd.to_datetime(tb['date'])

tb['rfy'] = tb.avba/100
tb['rfm'] = ((1+(tb.avba)/100)**(1/12))-1

data_all = pd.merge(tb[['date','rfm', 'rfy']], data_all, on = 'date')

#%% process/add spx 

spx = pd.read_csv('variance-python/data/raw/spx/spx_monthly.csv')

spx.columns = ['date', 'vwred', 'vwrid', 'ewred', 'edrid', 'value', 'rtrnm']
spx['date'] = pd.to_datetime(spx['date'], format='%Y%m%d')

spx['rtrny'] = (1 + spx.rtrnm)**(12) - 1

data_all = pd.merge(spx[['date', 'rtrnm', 'rtrny']], data_all, on = 'date')

#%% calculate excess return

# take difference of log return - that is I think how it should be done
data_all['excessya'] = 12*np.log(1 + data_all.rtrnm) - np.log(1 + data_all.rfy)

# difference of absolute return log afterwards
data_all['excessyb'] = 12* np.log(1 + (data_all.rtrnm - data_all.rfm))

excess = data_all[['date', 'excessya', 'excessyb']]

data_rep = my_time_filter(excess, start_date, end_date)
print(data_rep.mean(axis = 0)*100)

data_precrisis = my_time_filter(excess, start_date, '2007-12-31')
print(data_precrisis.mean(axis = 0)*100)


#%% sorted


# calculate a monthly return for vwred, vwrid, ewred, edrid
#for i in range(1,5):
#    spx[('rtrnm_' + str(i))] = (spx.iloc[:,i] - spx.iloc[:,i].shift(1))/spx.iloc[:,i].shift(1)

# 'rtrnm_1', 'rtrnm_2', 'rtrnm_3', 'rtrnm_4'

# excess return

# same with annualized returns - first should be idetical to first overall
#data_all['excessyc'] = np.log(1 + data_all.rtrny) - np.log(1 + data_all.rfy)
#data_all['excessyd'] = np.log(1 + (data_all.rtrny - data_all.rfy))

# , 'excessyb', 'excessyc', 'excessyd'

# with the equiy/value weighted returns
#for i in range(1,5):
#    data_all[('excessya_' + str(i))] = 12*np.log(1 + data_all[('rtrnm_' + str(i))]) - np.log(1 + data_all.rfm)


# plots 

#plt.plot(data_all.date, data_all.rtrnm)
#plt.plot(data_all.date, data_all.rfm)
#plt.title('monthly returns')
#plt.show()

#plt.plot(data_all.date, data_all.rtrny)
#plt.plot(data_all.date, data_all.rfy)
#plt.title('annualized monthly returns')