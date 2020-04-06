# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 10:00:10 2020

@author: Sophia
"""

def fib2(n):  
# include a short description: return Fibonacci series up to n
    result = []
    a, b = 0, 1
    while a < n:
        result.append(a)
        a, b = b, a+b
    return result

# it is important that the functions we create end with a return statement
