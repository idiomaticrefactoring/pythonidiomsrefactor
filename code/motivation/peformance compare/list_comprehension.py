import timeit


import numpy as np

code='''
t = []
for i in range(10000):
    t.append(i)
'''
total_time_1 = np.mean(
    timeit.repeat(code,
                  repeat=3, number=1000))
code='''
t= [i for i in range(10000)]
'''
total_time_2 = np.mean(
    timeit.repeat(code,

                  repeat=3, number=1000))
print("time1: ",total_time_1,total_time_2,total_time_1/total_time_2)