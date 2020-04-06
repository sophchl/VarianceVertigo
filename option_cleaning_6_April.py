# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 18:55:29 2020

@author: Attilio Nicoli
"""

#IN THIS FILE I WANT TO CLEAN THE OPTIONS

#import some random packages


import pandas as pd  

from numpy import nan


#import dataset
options=pd.read_csv (r'\\PC-NICOLI\Users\Attilio Nicoli\Documents\MATLAB\AQF\Dataset\option first two months.csv')

#delete useless variables downloaded without any good reason

options = options.drop(['index_flag','issuer','exercise_style'], axis=1)


#delete 'volume' and 'open interest' because we don't need them anymore

options = options.drop(['volume','open_interest'], axis=1)

#define 'average price' as the mean between 'best_bid' and 'best_offer'

options['option_price']=(options['best_bid']+options['best_offer'])/2

#delete 'best_bid' and 'best_offer' because we don't need them anymore

options = options.drop(['best_bid','best_offer'], axis=1)


#filter gamma=>0 or gamma==nan

options = options[(options['gamma'] >= 0) | (options['gamma']==nan)] 

#delete 'gamma' because we don't need it anymore

options = options.drop(['gamma'], axis=1)

#filter delta<=0 for put options and delta>=0 for call options (I don't know how to set the nan check for deltas, but in this case it seems that it is not important)

options = options[((options['cp_flag'] == 'P') & (options['delta']<=0)) | ((options['cp_flag'] == 'C') & (options['delta']>=0))] 


#delete 'delta' because we don't need it anymore

options = options.drop(['delta'], axis=1)

#filter 'average_price'>=0.375

options = options[options['option_price'] >= 0.375] 

#divide the strike by 1000 (I don't know why they multiplied it by 1000)

options['strike_price'] = options['strike_price']/1000

#define moneyness

options['moneyness'] = options['strike_price']/options['forward_price']

#delete ITM options filtering puts with moneyness below 1.03 and calls with moneyness above 0.97

options = options[((options['cp_flag'] == 'P') & (options['moneyness']<1.03)) | ((options['cp_flag'] == 'C') & (options['moneyness']>=0.97))] 

#
#TO SET 1-5 OF SECTION 3 OF 'No Arbitrage Constraints' I need reliable risk-free rates
#


#filter last_date+1>=date so that we delete options not traded for 2 days in a row

options = options[options['last_date']+1 >= options['date']] 


#define a list with all the arbitrage trading days, which are the days with less than 2 otm calls and 2 otm puts
#HONESTLY I DON'T KNOW IF IT IS THE BEST WAY TO DO IT
trading_days=[]
no_otm_days=[]

#create a list trading_days not repeat the same day more times for the same option

for day in options['date']:
    if day not in trading_days:
        trading_days.append(day)
        

#IT'S TERRIBLE THAT 10 REFERS TO MONEYNESS AND 4 TO CP_FLAG. I WANT TO FIND AN EASIER WAY TO EXPRESS THAT
   
#I need this indeces to make the code as much understandable as possible    
    
index_tuple_moneyness=options.columns.get_loc("moneyness")+1
index_tuple_cp_flag=options.columns.get_loc("cp_flag")+1

    
#check every day     
for day in trading_days:
    #at the beginning we don't have otm puts and calls
    c_otm_puts,c_otm_calls=0,0
    #I want to do a for loop for every option in this day (sorry for the bad code but I copy-pasted from internet)
    for option in options.loc[options['date'] == day].itertuples():
        # if we have a call with moneyness greater than 1 
        if option[index_tuple_moneyness]>1 and option[index_tuple_cp_flag]=='C':
            #then we have one more otm call
            c_otm_calls += 1
        #else, if we have a put wit moneyness lower than 1
        elif option[index_tuple_moneyness]<1 and option[index_tuple_cp_flag]=='P':
        #then we have one more otm put
            c_otm_puts += 1
        #if we don't have at least two otm calls and two otm puts
    if c_otm_puts<= 2 or c_otm_calls<=2:
        #this day is an arbitrage day
        no_otm_days.append(day)
    
   
#delete every option in a no_otm_day
        
options=options[~options['date'].isin(no_otm_days)]





#I need this indeces to make the code as much understandable as possible    

index_tuple_strike_price=options.columns.get_loc("strike_price")+1
index_tuple_maturity=options.columns.get_loc("exdate")+1
index_tuple_option_price=options.columns.get_loc("option_price")+1
index_tuple_option_ID=options.columns.get_loc("optionid")+1


#the next part of code is related to calendar arbitrage. To understand the code better, I advise you to read what this kind of arbitrage is before continuing 

#check every day
for day in trading_days:
    #define a set for strikes
    strikes_set=set()
    #define a list for options which will be used for comparisons
    options_list=[]
    #define a list for options that creates calendar arbitrage opportunities
    calendar_arbitrage_ids=[]
    #again a terrible loop for every option in this day
    for option in options.loc[options['date'] == day].itertuples():
        #if the strike of the option appears for the first time  
        if option[index_tuple_strike_price] not in strikes_set:
            #then I don't need to compare anything and I just add this strike to strikes_set
            strikes_set.add(option[index_tuple_strike_price])
        #in this case there is possibility of calendar arbitrage
        else:
            #loop for every options analyzed so far (I use derivative instead of option to differentiate the loops)
            for derivative in options_list:
                #if they create calendar arbitrage (very long but be patient)
                if option[index_tuple_strike_price]==derivative[index_tuple_strike_price] and (option[index_tuple_maturity]-derivative[index_tuple_maturity])*(option[index_tuple_option_price]-derivative[index_tuple_option_price])<0 and (option[index_tuple_cp_flag]==derivative[index_tuple_cp_flag]):
                    #add the ID of the option in analysis to the calendar_arbitrage_ids
                    calendar_arbitrage_ids.append(option[index_tuple_option_ID])
                    #add the ID of the derivative to the calendar_arbitrage_ids
                    calendar_arbitrage_ids.append(derivative[index_tuple_option_ID])
                    
        #once we have checked the option, we can add it for further comparisons            
        options_list.append(option)
    #at the end of every day we delete every option of that day such that his ID is in calendar arbitrage (so I 'save' the options such that they are not in calendar_arbitrage_ids OR they are related to this day)
    options=options[(~options['optionid'].isin(calendar_arbitrage_ids)) | (options['date']!=day)]   





