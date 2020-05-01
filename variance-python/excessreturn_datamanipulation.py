# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 09:07:17 2020

@author: Sophia

input:
output:
    
"""

#%% load dependencies

import numpy as np
import pandas as pd

#%% set parameters

data_all = pd.DataFrame()
data_all['date'] = pd.date_range('1996-01-01', '2020-03-31', freq = 'D').tolist()

start_date_paper = '1996-09-30'
end_date_paper = '2015-03-31'

#%% define functions

def my_time_filter(df, start_date, end_date):
    after_start_date = df['date'] >= start_date
    before_end_date = df['date'] <= end_date
    between_dates = after_start_date & before_end_date
    filtered_df = df[between_dates]
    return(filtered_df)

#%% process/add tbill (tb)

tb = pd.read_csv('data/raw2/tbill/rf3m.csv',)

print(tb.columns)
tb.columns  = ['ident', 'date', 'bidytm', 'askytm', 'nomytm']
tb['avba'] = (tb.bidytm + tb.askytm)/2
tb['date'] = pd.to_datetime(tb['date'])

tb['rfy'] = tb.avba/100
tb['rfm'] = ((1+(tb.avba)/100)**(1/12))-1

data_all = pd.merge(tb[['date','rfm', 'rfy']], data_all, on = 'date')

#%% process/add spx 

spx = pd.read_csv('data/raw2/spx/spx_monthly.csv')

spx.columns = ['date', 'vwred', 'vwrid', 'ewred', 'edrid', 'value', 'rtrnm']
spx['date'] = pd.to_datetime(spx['date'], format='%Y%m%d')

spx['rtrny'] = (1 + spx.rtrnm)**(12) - 1

data_all = pd.merge(spx[['date', 'rtrnm', 'rtrny']], data_all, on = 'date')

#%% calculate excess return

# take difference of log return - that is I think how it should be done
data_all['excessya'] = 12*np.log(1 + data_all.rtrnm) - np.log(1 + data_all.rfy)

# difference of absolute return and take log afterwards (just to check if authors maybe did that)
data_all['excessyb'] = 12* np.log(1 + (data_all.rtrnm - data_all.rfm))

excess = data_all[['date', 'excessya', 'excessyb']]

data_rep = my_time_filter(excess, start_date_paper, end_date_paper)
print(data_rep.mean(axis = 0)*100)

data_precrisis = my_time_filter(excess, start_date_paper, '2007-12-31')
print(data_precrisis.mean(axis = 0)*100)

# use excessya because computation makes more sense and both numbers are different from paper results
excess.index = excess['date']
excess = excess.drop(['excessyb', 'date'], axis = 1)


#%% save results

excess.to_csv("data/processed/excessreturn/excessreturn.csv")

#%% still guessing what is the right tbill...

test = pd.read_csv("data/raw2/tbill/rfdaily2.csv",)
col_names_wharton = test.columns
col_names_real = ['ident', 'KYCRSPID', 'date_treasury', 'date_maturity', 'coupon_rate', 'date_first_elcall', 'issue_type', 'date_first_bank_el', 'CALDT', 'bid', 'ask', 'nominal', 'return']
test.columns = col_names_real

examine_dates = test[['KYCRSPID', 'date_treasury', 'date_maturity', 'date_first_elcall', 'date_first_bank_el', 'CALDT']]
examine_dates2 = examine_dates[:]

examine_dates.index = pd.to_datetime(examine_dates['CALDT'])
examine_dates = examine_dates.drop(['date_first_bank_el', 'date_first_elcall', 'CALDT', 'date_treasury', 'KYCRSPID'], axis = 1)
examine_dates = examine_dates.sort_index()

examine_dates2.index = pd.to_datetime(examine_dates2['date_treasury'])
examine_dates2 = examine_dates2.drop(['date_first_bank_el', 'date_first_elcall', 'CALDT', 'date_treasury', 'KYCRSPID'], axis = 1)
examine_dates2 = examine_dates2.sort_index()

test.index = pd.to_datetime(test.date.astype(int), format = "%Y%m%d")
test = test.drop(['date'], axis = 1)
test['mat_date'] = pd.to_datetime(test['mat_date'])
