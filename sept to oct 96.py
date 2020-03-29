# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 15:14:43 2020

@author: Attilio Nicoli
"""

import math
import pandas as pd  
import numpy as np  
import csv

#intraday_test=pd.read_csv (r'C:\Users\Attilio Nicoli\Desktop\intraday shit\sept_30_1996 to oct_30_1996.csv')
#
#intraday_test_without_dates=pd.DataFrame(intraday_test, columns= ['BID'])
#
#intraday_test_without_dates=np.array(intraday_test_without_dates)
#
#print((intraday_test_without_dates[9184]-intraday_test_without_dates[2])/intraday_test_without_dates[2])


intraday_test1=pd.read_csv (r'C:\Users\Attilio Nicoli\Desktop\intraday shit\oct_31_1996 to nov_30_1996.csv')

intraday_test1_without_dates=pd.DataFrame(intraday_test1, columns= ['BID'])

intraday_test1_without_dates=np.array(intraday_test1_without_dates)

print((intraday_test1_without_dates[13658]-intraday_test1_without_dates[2])/intraday_test1_without_dates[2])


