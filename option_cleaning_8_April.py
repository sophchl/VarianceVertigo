# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 18:55:29 2020

@author: Attilio Nicoli
"""

#IN THIS FILE I WANT TO CLEAN THE OPTIONS
#only the left part of (2.63) of financial engineering script is missing (and his put's version) but it's probably too difficult.

#import some random packages

from datetime import datetime
import pandas as pd  
import numpy as np
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


#delete 'last_date'

options =  options.drop(['last_date'], axis=1)

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


del no_otm_days
del c_otm_puts
del c_otm_calls

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


del derivative, option, day, calendar_arbitrage_ids, options_list, strikes_set


#import risk-free for further no arbitrage conditions

risk_free=pd.read_csv (r'\\PC-NICOLI\Users\Attilio Nicoli\Documents\MATLAB\AQF\Dataset\rf3m.csv')



#the time format is terrible, so I have to turn it into datetime

risk_free['date'] = pd.to_datetime(risk_free['MCALDT'])




#turn date into an integer (so it's almost comparable with the options)

risk_free['date'] = pd.to_datetime(risk_free['date'], format='%Y-%m-%d').dt.strftime("%Y%m%d")

#we only care for the month

risk_free['date']=risk_free['date'].astype('int64')//100


# since we don't have daily risk free but only annualized monthly risk free, what I thought is to consider for every day in the month t: r_daily_t= (1+r_t)^(1/252)-1, where r_t is the original risk-free rate
# here I work with 'TMBIDYTM' but changing it with another column you can use a different one (3 choices in this dataset)

risk_free['TMBIDYTM']=(1+risk_free['TMBIDYTM']/100)**(1/252)-1

#THIS LINE WORKS ONLY ON THIS CODE BECAUSE I NEED ONLY THE FIRST TWO MONTHS, BE CAREFUL

risk_free=risk_free[:2]


#I want to create a column 'risk_free' for the options, so I need to turn some dataframes into arrays to change their values and then use them for the daily risk-free


# daily dates from options
dd_dates=np.array(options['date'])
# monthly dates from risk-free
months=np.array(risk_free['date'])

#I need to get the risk-free rate
risk_free_monthly=np.array(risk_free['TMBIDYTM'])

#we don't need the risk_free anymore

del risk_free


#initialize a float in which I will store the risk-free
risk_free_daily=np.zeros(len(options))

#I don't know why I had to do this, but dd_dates[0] is equal to zero without any sense (THIS IS A BIG ISSUE BECAUSE WE MIGHT FACE PROBLEMS WITHOUT NOTICING THEM WHEN WE WILL DEAL WITH THE ENTIRE DATASET )
dd_dates[0]=dd_dates[1]


#idea: we start with the first value of months and, for every day in the options, we give to that day the 'dayialized' risk_free owned by the respecrive month

#index for the months
index_month=0
#loop for every option
for i in range(len(options)):
    #if the monrh of that option is equal to the month under analysis
    if dd_dates[i]//100 == months[index_month]:
        # the risk_free associated to that option is equal to the risk_free of that month
        risk_free_daily[i]=risk_free_monthly[index_month]
    #otherwise    
    else:
        #it means that the 'new' option is in the newt month, so we change month
        index_month += 1
        #and do the same with the new month
        risk_free_daily[i]=risk_free_monthly[index_month]


#we define a new column for the risk_free
options['risk_free']=risk_free_daily


del risk_free_monthly,index_month,dd_dates,i,months, risk_free_daily


#we define a function to compute the distance between the day t and the day T

def time_to_maturity(t,T):
    date_t = datetime.strptime(str(t), '%Y%m%d')
    date_T = datetime.strptime(str(T), '%Y%m%d')
    return (date_T-date_t).days




index_tuple_forward=options.columns.get_loc('forward_price')+1
index_tuple_risk_free=options.columns.get_loc('risk_free')+1
index_tuple_date=options.columns.get_loc('date')+1

#for every day
for day in trading_days:
    #define a list for options that creates butterfly spread arbitrage
    arbitrage_ids=[]
    #again a terrible loop for every option in this day
    for option in options.loc[options['date'] == day].itertuples():
        # if inequality (4) or inequality (3) of section 3 of 'No-arbitrage constraints' doesn't hold this call creates an arbitrage on this day
        if option[index_tuple_cp_flag]== 'C' and (option[index_tuple_option_price]>option[index_tuple_forward]*np.exp(-option[index_tuple_risk_free]*time_to_maturity(option[index_tuple_date],option[index_tuple_maturity])) or option[index_tuple_option_price]<max(0,(option[index_tuple_forward]-option[index_tuple_strike_price])*np.exp(-option[index_tuple_risk_free]*time_to_maturity(option[index_tuple_date],option[index_tuple_maturity])))):
            arbitrage_ids.append(option[index_tuple_option_ID])
        # if inequality (5) of section 3 of 'No-arbitrage constraints' doesn't hold this put creates an arbitrage on this day    
        if option[index_tuple_cp_flag]== 'P' and option[index_tuple_option_price]<max(0,(option[index_tuple_strike_price]-option[index_tuple_forward])*np.exp(-option[index_tuple_risk_free]*time_to_maturity(option[index_tuple_date],option[index_tuple_maturity]))):
            arbitrage_ids.append(option[index_tuple_option_ID])
    #we delete every option on this day that creates arbitrage        
    options=options[(~options['optionid'].isin(arbitrage_ids)) | (options['date']!=day)]    
  


#I am going to deal with (2.63) (only the right part, the left one is so far too difficult for me) and (2.64) of the financial engineering script for both puts and calls. 
#for (2.63) you can show that for the puts the opposite inequality holds, while for (2.64) the same inequality holds.
#for (2.64) there is one other factor to take into consideration, we'll see it later.
    
#The idea is, for every day, to divide calls and puts.
#for every call in this day, we collect every maturity
#for every maturity, we collect every call with that maturity
#we sort this vector from the smallest to the biggest strike price
#we can 'easily' check possible arbitrages with for loops.
#a similar argument holds for the puts

#p.s. (*call*) and (*put*) are technical conditions, if you need to understand them, I will explain everything.


#for every day    
for day in trading_days:
    #we define a list for the bad IDs of this day
    arbitrage_ids=[]
    #we select the calls of this day
    daily_calls=options[(options['date'] ==day) & (options['cp_flag']=='C')]
    #we define a list for the maturities of the calls of this day
    maturities_call_list=[]
    #we do a loop on daily_calls to gather all the maturities and store them in maturities_call_list
    for option in daily_calls.itertuples():
        if option[index_tuple_maturity] not in maturities_call_list:
            maturities_call_list.append(option[index_tuple_maturity])
    #for every maturity T
    for T in maturities_call_list:
        #we define a dataframe with the calls of this day with maturity T
        calls_sorted=daily_calls.loc[options['exdate'] ==T]
        #we sort it from bottom to up
        calls_sorted=calls_sorted.sort_values(by=['strike_price'])
        #we define a counter for the following for loop.
        #in this way we know if we can compare two or three calls
        c_butt=0
        #we define these variables for the next loop
        last_price=0
        last_ID=0
        last_strike_price=0
        last_but_one_ID=0
        last_but_one_price=0
        last_but_one_strike_price=0
        #for every (sorted) call with maturity T on this day
        for call in calls_sorted.itertuples():
            #if it's not the first call of the loop
            if c_butt > 0:
                #if (2.63) doesn't hold
                if call[index_tuple_option_price]>last_price:
                    #this call creates an arbitrage
                    arbitrage_ids.append(call[index_tuple_option_ID])
                    #the last one in the loop does it too
                    arbitrage_ids.append(last_ID)
                #if this is exactly the second call of the loop    
                if c_butt == 1:
                    #we define the last but one ID as the previous last
                    last_but_one_ID=last_ID
                    #the same for the price
                    last_but_one_price=last_price
            #if this is at least the third call of the loop        
            if c_butt > 1:
                # if (2.64) doesn't hold and (*call*) holds the butterfly spread is negative
                if call[index_tuple_option_price]-2*last_price+last_but_one_price<0 and call[index_tuple_strike_price]+last_but_one_strike_price<=2*last_strike_price:
                    #so all the calls involved create an arbitrage
                    arbitrage_ids.append(call[index_tuple_option_ID])
                    arbitrage_ids.append(last_ID)
                    arbitrage_ids.append(last_but_one_ID)
                    
                #we update the parameters before the next call (in particular, here is that the last becomes the last but one)  
                last_but_one_ID=last_ID
                last_but_one_price=last_price
                last_but_one_strike_price=last_strike_price
            #the current call becomes the last one, when the next call comes.
            #So, we update the parameters
            last_ID=call[index_tuple_option_ID]  
            last_price=call[index_tuple_option_price]
            last_strike_price=call[index_tuple_strike_price]
            #we update the counter
            c_butt += 1
    
    #still in the same day, we do a similar work for the puts (I will focus only in the differences)
    maturities_put_list=[]
    daily_puts=options[(options['date'] == day) & (options['cp_flag']=='P')]        
    for option in daily_puts.itertuples():
        if option[index_tuple_maturity] not in maturities_put_list:
            maturities_put_list.append(option[index_tuple_maturity])
    for T in maturities_put_list:
        puts_sorted=daily_puts.loc[options['exdate'] ==T]
        puts_sorted=puts_sorted.sort_values(by=['strike_price'])
        c_butt=0
        last_price=0
        last_ID=0
        last_strike_price=0
        last_but_one_ID=0
        last_but_one_price=0
        last_but_one_strike_price=0
        indeces=puts_sorted.index
        for put in puts_sorted.itertuples():
            if c_butt > 0:
                #notice that the inequality is the opposite
                if put[index_tuple_option_price]<last_price:
                    arbitrage_ids.append(put[index_tuple_option_ID])
                    arbitrage_ids.append(last_ID)
                    
                if c_butt == 1:
                    last_but_one_ID=last_ID
                    last_but_one_price=last_price
            if c_butt > 1:
                # if (2.64) for puts doesn't hold and (*puts*) holds the butterfly spread is negative
                if put[index_tuple_option_price]-2*last_price+last_but_one_price<0 and put[index_tuple_strike_price]+last_but_one_strike_price>=2*last_strike_price:
                    arbitrage_ids.append(put[index_tuple_option_ID])
                    arbitrage_ids.append(last_ID)
                    arbitrage_ids.append(last_but_one_ID)
                    
                    
                last_but_one_ID=last_ID
                last_but_one_price=last_price
                last_but_one_strike_price=last_strike_price
            last_ID=put[index_tuple_option_ID]  
            last_price=put[index_tuple_option_price]
            last_strike_price=put[index_tuple_strike_price]
            c_butt += 1     
    #we delete every option (put or call) that creates arbitrage on this day
    options=options[(~options['optionid'].isin(arbitrage_ids)) | (options['date']!=day)]
    


#we delete every useless variable

del T, arbitrage_ids, c_butt, call, calls_sorted, daily_calls, daily_puts, day, last_ID, last_but_one_ID,last_but_one_price,last_but_one_strike_price,maturities_call_list,maturities_put_list,option,put,puts_sorted, last_price,last_strike_price
    
    
    




