# -*- coding: utf-8 -*-
"""
Created on Sat May  2 19:20:49 2020

@author: Sophia
"""

#%% load dependencies

import os
import pandas as pd


#%% import data (aggregated)

names_dataframes = ['h01', 'h02', 'h03', 'h06', 'h09', 'h12']
data_directory_vrp = "data/processed/vrp/"
list_vrp_data = []

for file in os.listdir(data_directory_vrp):
    filename = data_directory_vrp + file
    df = pd.read_csv(filename, index_col = 0)
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df['skw'] = df.vrpu - df.vrpd
    list_vrp_data.append(df)
    
names_dataframes = ['k01', 'k02', 'k03', 'k06', 'k09', 'k12']
data_directory_return = "data/processed/excessreturn/"
list_return_data = []

for file in os.listdir(data_directory_return):
    if file.startswith('k'):
        filename = data_directory_return + file
        df = pd.read_csv(filename, index_col = 0)
        df.index = pd.to_datetime(df.index)
        list_return_data.append(df)
        continue
    else:
        continue
    
#%% import data (unaggregated)

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

#%% use the aggregated data h=k=1 for summary statistics

vrp = list_vrp_data[0]*100
vrp_report = vrp[['vrp', 'vrpu', 'vrpd', 'rvu', 'rvd', 'ivu', 'ivd']]
excess = list_return_data[0]*100

report = pd.merge(vrp_report, excess, on = "date")

#%%

file_3 = open("results/tables/summarystatistics.tex", "a")
file_3.write(report.describe().to_latex())
file_3.close() 
