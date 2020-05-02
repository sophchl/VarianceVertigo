#import data
h1= read.csv("/Users/sfb/Desktop/GitHub/VarianceVertigo/variance-python/data/processed/models/h1.csv")
h3= read.csv("/Users/sfb/Desktop/GitHub/VarianceVertigo/variance-python/data/processed/models/h3.csv")
h6 = read.csv("/Users/sfb/Desktop/GitHub/VarianceVertigo/variance-python/data/processed/models/h6.csv")
excess= read.csv("/Users/sfb/Desktop/GitHub/VarianceVertigo/variance-python/data/processed/excessreturn/excessreturn_daily.csv") 

var=h3 #choose dataset wrt accumulating horizon

#NB ?? we should accumulate also the excess returns wrt h 

#get common timeframes
data=merge(excess, var, by.x = 'date', by.y= 'X')
data=na.omit(data) 

#define var for regressions
h=3 #choose h
y=data$excess_return/h  #the paper uses this scaling
X1=data$vrpd
window=as.integer(dim(data)[1]/2) #as defined in the paper

# expanding window regression
library(rollRegres)
roll =roll_regres(y ~ X1, data, width = window, do_downdates=FALSE,do_compute = c("sigmas", "r.squareds", "1_step_forecasts"))

#compute some statistics
colMeans(roll$coefs, na.rm = TRUE) #robust regression estimates = average coefficients of the model
mean(roll$r.squareds, na.rm = TRUE) #avg: [h=6: R^2=2.99%] [h=1: R^2= 4.15%] [h=3: R^2= 4.68%]
#calculate RMSE --> se how accurate forecast is 
RMSE = function(predicted, observed){sqrt(mean((predicted - observed)^2,na.rm = TRUE))}

predicted=roll$one_step_forecasts
observed=X1
RMSE(predicted, observed)  # [h=6: RMSE=0.77%] [h=1: RMSE=0.25%] [h=3: RMSE=0.34%]we have good out of sample predictions

#best results for h=1, h=3 (R^2 and RMSE)

#NB:
#1. if we want to construc t/F-tests we need to correct the roll$sigmas for serial correlation (eg. HAC --> use sandwich package)
#2. only possible to forecast ONE period ahead. We cannot evaluate if our models permorm best at a certain prediction horizon (eg. one-quarter ahead as stated in paper)
#3. compare outsmaple R2 with in-sample R2 (Sophia) and make table (eg. TAB 14 in paper)
#4 we should accumulate also the excess returns wrt h --> we only have monthly (h=1)

