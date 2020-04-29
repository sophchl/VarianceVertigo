#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 18:10:26 2020

@author: sfb
"""

#%% setup
import os
import numpy as np
import pandas as pd
import datetime as dt
from collections import defaultdict
from matplotlib import pyplot

#%% functions needed

def separate_tradingday_overnight(data):
    day = data[(data.index.time > dt.time(9,30,0)) & 
               (data.index.time < dt.time(16,0,0))]
    nightindex = data.index.difference(day.index)
    night = data.loc[nightindex,]
    return(day, night)
    
#%% loop over all files in directory to import the data

#data_directory = "data/raw/spxhf"
data_directory= "/Users/sfb/Desktop/ETH:UZH/SPRING SEMESTER/AQF-Applied Quantitative Finance/Data/HF SP500/prova"

list_dataframes = []

for file in os.listdir(data_directory):
    if file.endswith('.csv'):
        filename = data_directory + "/" + file
        df = pd.read_csv(filename, )
        list_dataframes.append(df)
        continue
    else:
        continue
    
#%% Nikola's Data
HF= pd.read_csv("/Users/sfb/Desktop/ETH:UZH/SPRING SEMESTER/AQF-Applied Quantitative Finance/Data/HF SP500/Nikola/SPY.csv")
HF.index=pd.to_datetime(HF.time, format = '%Y-%m-%d %H:%M:%S')
HF['date_time'] = HF.index
HF['date'] = pd.to_datetime(HF['date_time'], format='%Y%m%d').dt.date
HF['time'] = pd.to_datetime(HF['date_time'], format='%Y:%M:%D').dt.time

#%% create one big dataframe, sort by date and time, separate day and night

spx = pd.concat(list_dataframes)
spx.columns = ['symbol', 'date', 'time', 'bid','offer']
spx = spx.drop(['symbol'], axis = 1)
spx_datetime = spx['date'].astype(str) + ":" + spx['time']
spx.index = pd.to_datetime(spx_datetime, format = '%Y%m%d:%H:%M:%S')
spx['date'] = pd.to_datetime(spx['date'], format='%Y%m%d').dt.date
spx['time'] = pd.to_datetime(spx['time'], format='%H:%M:%S').dt.time

spx = spx.sort_index()

#%% average bid ask quotes
col = HF.loc[: , "open":"close"]
HF['level'] = col.mean(axis=1)

col2 = spx.loc[: , "bid":"offer"]
spx['level'] = col2.mean(axis=1)

#%% clean data
# check for douplicates and missings: 
np.sum(spx.isnull()) #No Missing Values in the dataset BUT there are some missing Days (eg. 08/01/2000 and 09/01/2000)

spx=spx[np.all(spx != 0, axis=1)]
spx = spx[(spx['date'] != spx['date'].shift()) | (spx['time'] != spx['time'].shift())] 
#there are some duplicate entries (same day and same time stamp) that mess up with the computation of returns.
#I have only kept the first of the duplicate entries. Maybe there is a better way to deal with this?

day, night = separate_tradingday_overnight(spx)
col3 = day.loc[: , "bid":"offer"]
day['level'] = col3.mean(axis=1)

#%% OPTION A: 1-min averages and then select 5th min
#selecting values 
day1min = day.resample('1T').mean() #Downsample into 1 minute bins and average over each bin.
day1min['date_time'] = day1min.index
day1min['date'] = pd.to_datetime(day1min['date_time'], format='%Y%m%d').dt.date
day1min['time'] = pd.to_datetime(day1min['date_time'], format='%H:%M:%S').dt.time

day_1min, night_1min = separate_tradingday_overnight(day1min)

fivemin = np.arange(dt.datetime(2000,1,3), dt.datetime(2000,3,2), dt.timedelta(minutes = 5)).astype(dt.datetime)
fivemin = pd.DataFrame(index = fivemin)

spx5a = pd.merge(day1min, fivemin, right_index = True, left_index = True) 
spx5a=spx5a[spx5a['date'].isin(day['date'])] #dont consider weekends and holidays


#%% OPTION B: 5 min resample
#average of e.g. 8:30 are all values from 8:25 to 8:30 etc.
spx5b = day.resample('5T').median()
#spx5b =  spx5b[1:]
spx5b['date_time'] = spx5b.index
spx5b['date'] = pd.to_datetime(spx5b['date_time'], format='%Y%m%d').dt.date
spx5b['time'] = pd.to_datetime(spx5b['date_time'], format='%Y:%M:%D').dt.time

spx5b=spx5b[spx5b['date'].isin(day['date'])] #dont consider weekends and holidays

HF_5min=HF.resample('5T').median()
HF_5min['date_time'] = HF_5min.index
HF_5min['date'] = pd.to_datetime(HF_5min['date_time'], format='%Y%m%d').dt.date
HF_5min['time'] = pd.to_datetime(HF_5min['date_time'], format='%Y:%M:%D').dt.time
HF_5min=HF_5min[HF_5min['date'].isin(HF['date'])] #dont consider weekends and holidays

# continue with one of them -->> I use option B
mydata = spx5b

#%% plots
pyplot.plot(mydata.index,mydata.level)
pyplot.show()

pyplot.plot(HF_5min.index,HF_5min.level)
pyplot.show()

#%% calculate return and realized variances
mydata = HF_5min

mydata['return'] = np.log(((mydata.level - mydata.level.shift(1))/(mydata.level.shift(1)))+1) #added log 

mydata2 = (mydata[['return']]**2).groupby(mydata.index.date).sum() 
mydata2.columns = ['rv']

#pyplot.plot(mydata2.index,mydata2.rv)
#pyplot.show()

#%% OPTION 1: calculate overnight returns using first last obs for each day individually
d = defaultdict(list)
date_time= day['date'].astype(str) + " " + day['time'].astype(str)
for dte in date_time:
    key, _ = dte.split()
    d[key].append(dte)

open_=[] 
close=[]
for k,v in d.items():
    open_.append(min(v))
    close.append(max(v))
    print(min(v), max(v))

open_=pd.to_datetime(open_, format = '%Y%m%d %H:%M:%S')
close=pd.to_datetime(close, format = '%Y%m%d %H:%M:%S')

open_data=day.loc[open_,:]
open_data=open_data.iloc[1:,:]   
open_data.reset_index(drop=True, inplace=True)

close_data=day.loc[close,:]
close_data=close_data.iloc[:-1,:] 
close_data.reset_index(drop=True, inplace=True)  

overnight_ret= np.log(open_data.level)-np.log(close_data.level)


#%% OPTION 2: calculate overnight returns using retunrs at 9:35 and 15:55 everyday
open_=pd.DataFrame(mydata[(mydata['time'] == dt.time(9,35,0))])
open_.reset_index(drop=True, inplace=True)

close=pd.DataFrame(mydata[(mydata['time']== dt.time(16,00,0))])
close.reset_index(drop=True, inplace=True)

overnight_ret= pd.DataFrame(np.log(open_.level)-np.log(close.level).shift(1)).set_index(mydata2.index)

#i use option 2
mydata2['overnight_ret']=overnight_ret
mydata2['rv_tot'] = mydata2['rv'] + mydata2['overnight_ret']**2


#%% calculate upside and downside realized variance
k=0
mask = mydata['return'] < k
mydata_U = pd.DataFrame(mydata['return'].mask(mask))
mydata_D  = pd.DataFrame(mydata['return'].mask(~mask))

mydata2['rv_U']= (mydata_U[['return']]**2).groupby(mydata_U.index.date).sum()
mydata2['rv_D'] = (mydata_D[['return']]**2).groupby(mydata_D.index.date).sum()


mask2 = mydata2['overnight_ret'] < k
mydata_U_tot = pd.DataFrame(mydata2['overnight_ret'].mask(mask2))
mydata_D_tot  = pd.DataFrame(mydata2['overnight_ret'].mask(~mask2))
mydata_U_tot['overnight_ret']=np.nan_to_num(mydata_U_tot) 
mydata_D_tot['overnight_ret']=np.nan_to_num(mydata_D_tot)

mydata_U_tot.overnight_ret.iloc[0]=float('NaN')
mydata_D_tot.overnight_ret.iloc[0]=float('NaN')


mydata2['rv_U_tot'] = mydata2['rv_U'] + mydata_U_tot.overnight_ret**2
mydata2['rv_D_tot'] = mydata2['rv_D'] + mydata_D_tot.overnight_ret**2 

#pyplot.plot(mydata2.index,mydata2.rv_U_tot)
#pyplot.show()
#pyplot.plot(mydata2.index,mydata2.rv_D_tot)
#pyplot.show()

#%% apply scaling
sample_var= np.var(mydata2['rv_tot'])
mydata2['rv_scaled']= mydata2['rv_tot']/sample_var
sample_avg=np.mean(mydata2['rv_scaled'])

mydata2['rv_U_scaled']=(mydata2['rv_U_tot'] * sample_var) / (sample_avg)
mydata2['rv_D_scaled']=(mydata2['rv_D_tot'] * sample_var) / (sample_avg)
mydata2['rv_scaled']=mydata2['rv_U_scaled']+mydata2['rv_D_scaled']
mydata2['date'] = mydata2.index
mydata2['month'] = pd.to_datetime(mydata2['date'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m'))

#%% accumulating h=1 month
RV_cum=pd.DataFrame()
RV_cum['RV_U_cum']=mydata2['rv_U_scaled'].groupby(mydata2.month).sum()
RV_cum['RV_D_cum']=mydata2['rv_D_scaled'].groupby(mydata2.month).sum()
RV_cum['RV_tot_cum']=mydata2['rv_scaled'].groupby(mydata2.month).sum()

RV_cum.reset_index(drop=False, inplace=True)  

#pyplot.plot(RV_cum.month,RV_cum.RV_U_cum)
#pyplot.show()
#pyplot.plot(RV_cum.month,RV_cum.RV_D_cum)
#pyplot.show()
#pyplot.plot(RV_cum.month,RV_cum.RV_tot_cum)
#pyplot.show()
#%% accumulating h month (general)
#for months h=2,3,6,9,12,18,24 month
h = 2
RV_cum_h= RV_cum.groupby(RV_cum.index // h).sum()

#%% construction of P-exp (h=1 month)
h=1

E_RV_t=RV_cum.shift(h)

#%% construction of Q-exp


