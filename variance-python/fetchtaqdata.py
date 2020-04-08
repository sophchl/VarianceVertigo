# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:19:10 2020

@author: Sophia
"""

#%% installation and remarks

'''

installation of wrds:
    windows: in annaconda prompt: pip install wrds
    mac: same command in terminal (couldn't try this because I don't have mac)

helpful sources:
    documentation python at wrds: https://wrds-www.wharton.upenn.edu/pages/support/programming-wrds/programming-python/python-from-your-computer/
    taq dataset list: https://wrds-web.wharton.upenn.edu/wrds/tools/variable.cfm?library_id=56

remark1:
    The datasets are really big (20-50GB acc to documentation)!
    Hence I wrote a fct that returns a list of datasets, 
    so you can download smaller timeframes and we can concatenate at the end.    
    
remark2:
    wrds package offers 2 ways to download the datasets, get_table() and raw_sql()
    raw_sql() is more flexible but I did not yet find a way to aggregate
    the data to 5mim before downloading thus so far I use get_table()
    
remark3:
    taq changed reporting over the years :
    monthly (second-level data): 1993 - 2014
    daily (macrosecond-level data): 2001 - present
    
'''

#%% setup

import wrds
import numpy as np
import pandas as pd
import datetime as dt

def create_list_datasets(start_dt, end_dt, set_initials):
    list_datasets = []
    start_dt = start_dt
    end_dt = end_dt
    for n in range(((end_dt - start_dt).days)+1):
        next_day = (start_dt + dt.timedelta(n)).strftime("%Y%m%d")
        dataset = set_initials + next_day
        list_datasets.append(dataset)
    return(list_datasets)

#%% establish connection and save password

db = wrds.Connection(wrds_username='afqfs20')
db.create_pgpass_file()

#%% explore database

# look into the structure
db.list_libraries()
db.list_tables(library='taq')
db.describe_table(library='taq', table='cq_19960930')

# get the first 10 observations to see if it works 
test_name = 'cq_19960930'
test1 = db.get_table(library = "taq", table = test_name, columns = ['bid, ofr'], obs = 10)
test2 = db.raw_sql("select bid, ofr from taq." + test_name + " LIMIT 10")

# if this does not work, try uppercase, i.e. 'CQ_199960930')

#%% download the data until 2014

def download_data_before14(start_dt, end_dt, set_initials):
    
    datasets_in = create_list_datasets(start_dt, end_dt, set_initials)   
    datasets_out = []
    
    for i in datasets_in:
        data = db.get_table(library = "taq", table = i, columns = ['bid', 'ofr'])
        # this should be a pd.DataFrame with variables: SYMBOL,DATE,TIME,BID,OFR
        data.index = pd.to_datetime(data['DATE'].astype(str) + ":" + data['TIME'], format = '%Y%m%d:%H:%M:%S')
        data = data.drop(['SYMBOL', 'DATE', 'TIME'], axis = 1)
        data = data.resample('5T').mean()
        datasets_out.append(data)
        
    return(datasets_out)

# try 2 month
start_dt = dt.date(1996, 9, 30)
end_dt = dt.date(1996, 11, 30)
set_initials = 'cq_'

dataset_list1 = download_data_before14(start_dt, end_dt, set_initials)

dataset_result = pd.concat(dataset_list1)


#%% download the data after 2014

# not done yet

datasets2 = create_list_datasets(dt.date(2015, 1, 1), dt.date(2019, 12, 31), 'cqm_') 

#%% save dataset

dataset_result.to_csv('hfspx.csv')

#%% end session 

db.close()

#%% other

# list of available functions 
# =============================================================================
# db.close()
# db.connection()
# db.describe_table()
# db.get_table()
# db.list_tables()
# db.raw_sql()
# db.get_row_count()
# db.list_libraries()
# =============================================================================
