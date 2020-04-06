# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 10:00:10 2020

@author: Sophia
"""

#%% load dependencies

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#%% functions

def fib2(n):  
# include a short description: return Fibonacci series up to n
    result = []
    a, b = 0, 1
    while a < n:
        result.append(a)
        a, b = b, a+b
    return result

# it is important that the functions we create end with a return statement


def my_latex_table(object, tablename):
# a very short function that exports a table into our table file
# we can try to go with what is already installed, else: tabulate, PyLaTeX seems good
    pd.DataFrame(object).to_latex('results/tables/' + tablename + '.tex')
    print('the input was saved to: "results/tables/' + tablename + '.tex".')

def my_graphic_saver(object, graphicname):
# again a short function that exports a graphic into graphic file
# dependency: matplotlib.pylplot
    plt.plot(object)
    plt.savefig('results/graphics/' + graphicname + '.png')
    print('the input was saved to: "results/graphics/' + graphicname + '.png".')