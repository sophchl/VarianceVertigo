# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:19:10 2020

@author: Sophia
"""

# dont't run yet, confirm with Nikola beforehand

# setup
import wrds
db = wrds.Connection(wrds_username='afqfs20')
db.create_pgpass_file()

# test if pw is safeed, disconnect and reconnect
db.close()
db = wrds.Connection(wrds_username='afqfs20')

# start to look into the structure
db.list_libraries()
db.list_tables(library='taq')
# problem: looks like each day is available as one dataset
db.describe_table(library='taq', table='WCT_1993..')

# get the data
#get_table()
#raw_sql()
table_name = "enter table name here"

# first check how many observations there are
print(db.get_row_count('taq', table_name))

# get the first 10 observations to see if it works
data = db.get_table(library = "taq", table = table_name, columns = "", obs = 10)

# probably we will have to download the data in a loop
