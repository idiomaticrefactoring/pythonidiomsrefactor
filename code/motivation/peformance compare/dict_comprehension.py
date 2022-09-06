import timeit
import numpy as np
import time

a={i:i for i in range(1000)}
code='''
b = {v: k for k, v in a.items()}
'''
total_time_2 = np.mean(
    timeit.repeat(code,globals=globals(),

                  repeat=3, number=100000))
code='''
b = {}
for k, v in a.items():
     b[v]=k
'''
total_time_1 = np.mean(
    timeit.repeat(code,globals=globals(),
                  repeat=3, number=100000))

print("time1: ",total_time_1,total_time_2,total_time_1/total_time_2)