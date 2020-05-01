# -*- coding: utf-8 -*-
"""
Created on Fri May  1 17:18:15 2020

@author: Sophia

input: spy 5min data (from processed)
output: RV upside and downside, daily frequency (to processed)

"""

#%% load dependencies

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import os

#%% set parameters

start_date_paper = '1996-09-30'
end_date_paper = '2015-03-31'
end_date_crisis = '2007-12-31'

tradingdays_month = 21
h_month = [1,2,3,6,9,12]
k_month = [1,2,3,6,9,12]
k_days = k_month*tradingdays_month

#%% functions needed


#%% load data

names_dataframes = ['h01', 'h02', 'h03', 'h06', 'h09', 'h12']
data_directory_vrp = "data/processed/vrp/"
list_vrp_data = []

for file in os.listdir(data_directory_vrp):
    filename = data_directory_vrp + file
    df = pd.read_csv(filename, index_col = 0)
    list_vrp_data.append(df)
    
names_dataframes = ['k01', 'k02', 'k03', 'k06', 'k09', 'k12']
data_directory_return = "data/processed/excessreturn/"
list_return_data = []

for file in os.listdir(data_directory_return):
    if file.startswith('k'):
        filename = data_directory_return + file
        df = pd.read_csv(filename, index_col = 0)
        list_return_data.append(df)
        continue
    else:
        continue

ex_return = pd.read_csv("data/processed/excessreturn/excessreturn_daily.csv", index_col = 0)


#%% one-variable regressions

test1 = list_vrp_data[0]
test1['vrpu']
test2['vrpd']


model = LinearRegression()



