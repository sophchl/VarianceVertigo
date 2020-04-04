# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 11:32:13 2020

@author: Sophia
"""

#%% setup

import os
import numpy as np
import pandas as pd
import datetime as dt


#%% lopp over all files in directory to import the data

data_directory = "data/raw/spxhf"

list_dataframes = []

for file in os.listdir(data_directory):
    if file.endswith('.csv'):
        filename = data_directory + "/" + file
        df = pd.read_csv(filename, )
        list_dataframes.append(df)
        continue
    else:
        continue
    
#%% create one big dataframe, sort by date and time check for doublicates and missings

spx = pd.concat(list_dataframes)
spx.columns = ['symbol', 'date', 'time', 'bid']
spx['datetime'] = spx['date'].astype(str) + ":" + spx['time']
spx['datetime'] = pd.to_datetime(spx['datetime'], format = '%Y%m%d:%H:%M:%S')
spx['date'] = pd.to_datetime(spx['date'], format='%Y%m%d').dt.date
spx['time'] = pd.to_datetime(spx['time'], format='%H:%M:%S').dt.time

spx = spx.sort_values(by = 'datetime')

#%% average bid ask quotes

#spx['level'] = np.mean(spx['bid'], spx['offer'])

#%% 
