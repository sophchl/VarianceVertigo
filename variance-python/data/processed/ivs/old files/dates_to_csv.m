class(dates)
test = datenum(dates)
class(test)
%writematrix(test,"test.csv")
test2 = datestr(dates)
class(test2)
writematrix(test2,"dates.csv")