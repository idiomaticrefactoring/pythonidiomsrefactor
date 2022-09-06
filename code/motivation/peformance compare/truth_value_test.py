import timeit

import numpy as np

a=[]
code='''
if a==[]:
 pass
'''
total_time_1 = np.mean(
    timeit.repeat(code,globals=globals(),
                  repeat=3, number=10000000))
code='''
if not a:
 pass
'''
total_time_2 = np.mean(
    timeit.repeat(code,globals=globals(),

                  repeat=3, number=10000000))
print("time1: ",total_time_1,total_time_2,total_time_1/total_time_2)
