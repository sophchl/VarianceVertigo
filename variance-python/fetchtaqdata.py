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
    The datasets are really big (20-50GB per day acc to documentation)!
    
remark2:
    wrds package offers 2 ways to download the datasets, get_table() and raw_sql()
    raw_sql() is more flexible but I did not yet find a way to aggregate 5min data
    
remark3:
    taq changed reporting over the years :
    monthly (second-level data): 1993 - 2014
    daily (macrosecond-level data): 2001 - present
    
remark4:
    As I could not try if the code works, the idea of this code is to execute it section by section,
    continuing further down as long as no error occurs. If everything works I can make it a nicer function.
    
'''

#%% setup

import wrds
import numpy as np
import pandas as pd
import datetime as dt

#%% all functions needed

def create_list_datasets(start_dt, end_dt, set_initials):
    '''
    creates list with names of datasets within a given date range
    input: start_dt, end_dt: start, end date as dt.time(YYYY,M,D), set_initials: 'cq_' until 2014, 'cqm_' afterwards
    output: list of names of datasets (stings)
    '''
    
    list_datasets = []
    
    for n in range(((end_dt - start_dt).days)+1):
        next_day = (start_dt + dt.timedelta(n)).strftime("%Y%m%d")
        dataset = set_initials + next_day
        list_datasets.append(dataset)
    return(list_datasets)

def download_data_before14(start_dt, end_dt, set_initials):
    '''
    download datasets within a given daterange
    input: start_dt, end_dt: start, end date as dt.time(YYYY,M,D), set_initials: 'cq_' until 2014, 'cqm_' afterwards
    output: list of datasets aggregated to 5min
    '''
    
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

#%% establish connection and save password

# ENTER YOUR USERNAME HERE; A LINE SHALL OPEN ASKING FOR PASSWORD
db = wrds.Connection(wrds_username='enter username here')
db.create_pgpass_file()

#%% explore database

# run this try code before proceeding to the loop

# look into the structure
db.list_libraries()
db.list_tables(library='taq')
db.describe_table(library='taq', table='cq_19960930')

# get the first 10 observations to see if it works 
test_name = 'cq_19960930'
test1 = db.get_table(library = "taq", table = test_name, columns = ['bid, ofr'], obs = 10)
test2 = db.raw_sql("select bid, ofr from taq." + test_name + " LIMIT 10")

# if this does not work, try uppercase, i.e. 'CQ_199960930')
# or try library = 'taq/sasdata'

#%% download from the data until 2014

# ENTER HERE THE START AND END DATE TO DOWNLOAD (maybe try first 2 month, then increase window if it works)
start_dt = dt.date(1996, 9, 30)
end_dt = dt.date(1996, 11, 30)

# this should refer us to the right database
set_initials = 'cq_'

dataset_list1 = download_data_before14(start_dt, end_dt, set_initials)

dataset_result = pd.concat(dataset_list1)


#%% download the data after 2014

# not done yet, first see if the above works

# ENTER HERE THE START AND END DATE TO DOWNLOAD
start_dt = dt.date(2014, 1, 1)
end_dt = dt.date(2014, 3, 31)

# this should refer us to the right database
set_initials = 'cqm_'

datasets2 = create_list_datasets(start_dt, end_dt, set_initials) 

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
