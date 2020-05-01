# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 09:07:17 2020

@author: Sophia

input: daily and monthly spx returns, monthly 3m tbill rate data (from raw2)
output: daily and monthly excess returns (to processed)
    
"""

#%% load dependencies

import numpy as np
import pandas as pd
import datetime as dt

#%% define functions

def my_time_filter(df, start_date, end_date):
    after_start_date = df.index >= start_date
    before_end_date = df.index <= end_date
    between_dates = after_start_date & before_end_date
    filtered_df = df[between_dates]
    return(filtered_df)

def check_for_nans(data):
    # does nan check
    rows_w_nans = data[data.isnull().any(axis = 1)]
    number_nans = len(rows_w_nans)
    print('number of nans is:', number_nans, ' \n rows with nans are: \n', rows_w_nans)
    

#%% process/add tbill (tb)

# read tbill
tb = pd.read_csv('data/raw2/tbill/rf3m.csv',)
tb.columns  = ['ident', 'date', 'bidytm', 'askytm', 'nomytm']
tb.index = pd.to_datetime(tb['date'])
tb['avba'] = (tb.bidytm + tb.askytm)/2

# create monthly rf dataset (use only rfy)
tb['rfy'] = tb.avba/100
tb['rfm'] = ((1+(tb.avba)/100)**(1/12))-1
rf_monthly = tb[['rfy', 'rfm']]

# create daily rf dataset
tb['ln_rfd'] = np.log(1+tb.rfy)/(12*21)
rf_daily = tb[['ln_rfd']].resample('1D').sum()
rf_daily = rf_daily.replace(0, np.nan)
rf_daily = rf_daily.bfill()
rf_daily.columns = ['rf']

#%% process/add spx daily

spx = pd.read_csv('data/processed/spxhf/spx5min.csv', index_col = 0)
spx.index = pd.to_datetime(spx.index)

# calculate open and close
spx_daily = spx[spx.index.time == dt.time(9,30,0)][['mid']].resample('1D').sum()
spx_daily.columns = ['open']
spx_daily['close'] = spx[spx.index.time == dt.time(16,0,0)].mid.resample('1D').sum()

# now we have to remove weekends and non-tradingdays to calculate returns
spx_daily = spx_daily[spx_daily.index.isin(spx['date'])]

# check for nans and zeros
check_for_nans(spx_daily)
spx_daily[(spx_daily.open.eq(0) | spx_daily.close.eq(0))]

# 1 row 0, set to nan and interpolate it
spx_daily = spx_daily.replace(0, np.nan)
spx_daily['close'] = spx_daily['close'].interpolate()

# calculate returns
spx_daily['return'] = np.log(spx_daily['close']) - np.log(spx_daily['close']).shift(1)
spx_daily.index.name = "date"

#%% create one daily dataframe and create daily excess return (annualized)

all_daily = pd.merge(spx_daily['return'], rf_daily, on = "date")
all_daily['excess_return'] = 12*(all_daily['return'] - all_daily['rf'])

#%% process/add spx monthly

spx_monthly = pd.read_csv('data/raw2/spx/spx_monthly.csv')

spx_monthly.columns = ['date', 'vwred', 'vwrid', 'ewred', 'edrid', 'value', 'rtrnm']
spx_monthly.index = pd.to_datetime(spx_monthly['date'], format='%Y%m%d')

spx_monthly['rtrny'] = (1 + spx_monthly.rtrnm)**(12) - 1

#%% create one monthly dataframe and create monthly excess return

all_monthly = pd.merge(spx_monthly['rtrnm'], rf_monthly['rfy'], on = "date")

# take difference of log return 
all_monthly['excess_return'] = 12*np.log(1 + all_monthly.rtrnm) - np.log(1 + all_monthly.rfy)

start_date_paper = '1996-09-30'
end_date_paper = '2015-03-31'
end_date_crisis = '2007-12-31'

data_rep = my_time_filter(all_monthly, start_date_paper, end_date_paper)
print(data_rep.mean(axis = 0)*100)

data_precrisis = my_time_filter(all_monthly, start_date_paper, end_date_crisis)
print(data_precrisis.mean(axis = 0)*100)


#%% save results

all_daily.to_csv("data/processed/excessreturn/excessreturn_daily.csv")
all_monthly.to_csv("data/processed/excessreturn/excessreturn_monthly.csv")

#%% still guessing what is the right tbill...

'''

all_dates = pd.date_range('1996-01-01', '2020-04-30', freq = 'D').tolist()
all_dates = pd.DataFrame(index = all_dates)
all_dates.index.name = 'date'

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

#%% different dates
start = dt.date(1996,1,1)
end = dt.date(2020,3,1)
date_list = [end - dt.timedelta(days=x) for x in range((end-start).days)]

data_all = pd.DataFrame(columns = ['date'])
data_all['date'] = date_list

'''