# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# this is our main python file, all functions we created come together

#%% load our modules via import


#%% import the data 

#%% run the models

#%% plto the results

#%% robustness tests


#%% examples

# example on working with modules (main source: https://docs.python.org/3/tutorial/modules.html)

import example 

# show what functions are in a module
print(dir(example))

# execute the function fib2, assign to fibonacci
fibonacci = example.fib2(10)
print(fibonacci)

# example latex table and graphic outputs: save them to results!
example.my_latex_table(fibonacci, 'example_table')
example.my_graphic_saver(fibonacci, 'example_graphic')


    





