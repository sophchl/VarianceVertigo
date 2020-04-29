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

#%% create one big dataframe, sort by date and time, separate day and night

spx = pd.concat(list_dataframes)
spx.columns = ['symbol', 'date', 'time', 'bid','offer']
spx = spx.drop(['symbol'], axis = 1)
spx_datetime = spx['date'].astype(str) + ":" + spx['time']
spx.index = pd.to_datetime(spx_datetime, format = '%Y%m%d:%H:%M:%S')
spx['date'] = pd.to_datetime(spx['date'], format='%Y%m%d').dt.date
spx['time'] = pd.to_datetime(spx['time'], format='%H:%M:%S').dt.time

spx = spx.sort_index()

# check for douplicates and missings: 
np.sum(spx.isnull()) #No Missing Values in the dataset BUT there are some missing Days (eg. 08/01/2000 and 09/01/2000)

spx = spx[(spx['date'] != spx['date'].shift()) | (spx['time'] != spx['time'].shift())] 
#there are some duplicate entries (same day and same time stamp) that mess up with the computation of returns.
#I have only kept the first of the duplicate entries. Maybe there is a better way to deal with this?

day, night = separate_tradingday_overnight(spx)

#%% take only 5-min prices

# A: selecting values 
day1min = day.resample('1T').mean() #Downsample into 1 minute bins and average over each bin.
day1min['date_time'] = day1min.index
day1min['date'] = pd.to_datetime(day1min['date_time'], format='%Y%m%d').dt.date
day1min['time'] = pd.to_datetime(day1min['date_time'], format='%H:%M:%S').dt.time


fivemin = np.arange(dt.datetime(2000,1,3), dt.datetime(2000,3,2), dt.timedelta(minutes = 5)).astype(dt.datetime)
fivemin = pd.DataFrame(index = fivemin)

spx5a = pd.merge(day1min, fivemin, right_index = True, left_index = True) #NB. in this way there are some days that were not in the original dataset that pop up

# B: 5 min resample
# looks like average of e.g. 8:30 are all values from 8:25 to 8:30 etc.
spx5b = day.resample('5T').mean()
spx5b =  spx5b[1:]
spx5b['date_time'] = spx5b.index
spx5b['date'] = pd.to_datetime(spx5b['date_time'], format='%Y%m%d').dt.date
spx5b['time'] = pd.to_datetime(spx5b['date_time'], format='%Y:%M:%D').dt.time

# continue with one of them
mydata = spx5b

#%% average bid ask quotes
#spx['level'] = np.mean(spx['bid'], spx['offer'])


#%% calculate return and realized variances
mydata['return'] = np.log(((mydata.bid - mydata.bid.shift(1))/(mydata.bid.shift(1)))+1) #added log 

mydata2 = (mydata[['return']]**2).groupby(mydata.index.date).sum() 
mydata2.columns = ['rv']

#%% overnight returns 
#NB. because of the missing days in the dataset this code doesnt give one return for each day, but only for those
# available in the original dataset hence it doesnt work if the dataset has missing days

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

overnight_ret= np.log(open_data.bid)-np.log(close_data.bid).shift(1)


#%% overnight returns 
open_=pd.DataFrame(mydata[(mydata['time'] == dt.time(9,30,0))])
open_.reset_index(drop=True, inplace=True)

close=pd.DataFrame(mydata[(mydata['time']== dt.time(15,55,0))])
close.reset_index(drop=True, inplace=True)

overnight_ret= pd.DataFrame(np.log(open_.bid)-np.log(close.bid)).set_index(mydata2.index)
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

mydata2['rv_U_tot'] = mydata2['rv_U'] + mydata_U_tot.overnight_ret**2
mydata2['rv_D_tot'] = mydata2['rv_D'] + mydata_D_tot.overnight_ret**2


#np.sum(1-np.isnan(mydata_U['return'])) #1552 --> can be considered symmetrically distributed around k=0
#np.sum(1-np.isnan(mydata_D['return'])) #1681

#%% apply scaling
sample_var= np.var(mydata2['rv_tot'])
mydata2['rv_scaled']= mydata2['rv_tot']/sample_var
sample_avg=np.mean(mydata2['rv_scaled'])

mydata2['rv_U_scaled']=(mydata2['rv_U_tot'] * sample_var) / (sample_avg)
mydata2['rv_D_scaled']=(mydata2['rv_D_tot'] * sample_var) / (sample_avg)
mydata2['rv_scaled']=mydata2['rv_U_scaled']+mydata2['rv_D_scaled']

mydata2['date'] = mydata2.index
mydata2['month'] = pd.to_datetime(mydata2['month'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m'))

#%% accumulating

RV_U_cum=mydata2['rv_U_scaled'].groupby(mydata2.month).sum()
RV_D_cum=mydata2['rv_D_scaled'].groupby(mydata2.month).sum()
RV_cum=mydata2['rv_scaled'].groupby(mydata2.month).sum()

#%% construction of p exp
h=1

E_RV_t=RV_cum.shift(h)




