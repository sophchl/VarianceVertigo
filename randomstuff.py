# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:39:23 2020

@author: Attilio Nicoli
"""
import math
import pandas as pd  
import numpy as np  
import csv

essenpi = pd.read_csv (r'\\PC-NICOLI\Users\Attilio Nicoli\Documents\MATLAB\AQF\Dataset\S&P500_monthly_return.csv')  

essenpi_sophia=pd.read_csv (r'\\PC-NICOLI\Users\Attilio Nicoli\Documents\MATLAB\AQF\Dataset\spx2.csv')  



#CASE 1: I USE US_Treasury_and_inflation_indexes_90_days_monthly_return
risk_free=pd.read_csv (r'\\PC-NICOLI\Users\Attilio Nicoli\Documents\MATLAB\AQF\Dataset\US_Treasury_and_inflation_indexes_90_days_monthly_return.csv')
risk_free_without_dates=pd.DataFrame(risk_free, columns= ['t90ret'])

#CASE 2: I USE CRSP TREASURIES - Monthly Riskfree Series (3-month)
#risk_free=pd.read_csv (r'\\PC-NICOLI\Users\Attilio Nicoli\Documents\MATLAB\AQF\Dataset\CRSP TREASURIES - Monthly Riskfree Series (3-month).csv')


#CASE 2a: I USE TMBIDYTM

#risk_free_without_dates=pd.DataFrame(risk_free, columns= ['TMBIDYTM'])/1000

#CASE 2b: I USE TMASKYTM

#risk_free_without_dates=pd.DataFrame(risk_free, columns= ['TMASKYTM'])/1000




essenpi_whithout_dates=pd.DataFrame(essenpi, columns= ['sprtrn'])



#essenpi_whithout_dates['logsprtrn']=np.log1p(essenpi_whithout_dates['sprtrn'])

essenpi_whithout_dates=np.array(essenpi_whithout_dates)

risk_free_without_dates=np.array(risk_free_without_dates)

essenpi_xsreturn_without_dates=essenpi_whithout_dates-risk_free_without_dates


log_essenpi_xsreturn_without_dates=np.log(essenpi_xsreturn_without_dates+1)






#annualization of the mean
mean=np.mean(log_essenpi_xsreturn_without_dates)*12


#a=np.log1p()

##logreturns = np.math.log1p(logreturns['sprtrn'])
#print(logreturns-essenpi_whithout_dates)
##essenpi=np.array(essenpi)


