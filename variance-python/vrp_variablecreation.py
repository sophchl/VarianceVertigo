# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 10:43:08 2020

@author: Sophia

input:
output:
    
"""

#%% setup

import numpy as np
import pandas as pd
import datetime as dt
import scipy.io as sio

#%% set variables

#%% import dates and try to handle them

dates = sio.loadmat('data/processed/ivs/_dates.mat')

# looks like that is a dictionary

for i in dates.keys():
    print(i)
    print('contains')
    print(dates[i])

# looks like what we need is in 'None'
print('type of None is', type(dates['None']))
print(dates['None'])

# or in '__function_workspace__' ?
print('type of __function_workspace__ is', type(dates['__function_workspace__']))
print(dates['__function_workspace__'])

pd.DataFrame(dates['__function_workspace__'])

#%% import dates from numeric

dates = pd.read_csv('data/processed/ivs/dates.csv', header = None)
dates = dates.rename(columns={0:'dates'})
dates['dates'] = pd.to_datetime(dates['dates'])

#%% import the iv files

ivd = pd.read_csv("data/processed/ivs/IV_D_interpolated_030107_to_071015.csv", header = None)
ivu = pd.read_csv("data/processed/ivs/IV_U_interpolated_030107_to_071015.csv", header = None)

# we have to manually set headers becaut they are not contained in the csv files

ivd.columns = ['h1', 'h2', 'h3', 'h6', 'h9', 'h12']
ivu.columns = ['h1', 'h2', 'h3', 'h6', 'h9', 'h12']

#%% import the rv files

rv = pd.read_csv("data/processed/spxhf/spx5min.csv", index_col = 0)
    




