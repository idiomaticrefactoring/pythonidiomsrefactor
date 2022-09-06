import timeit

import numpy as np

a,b,c,d,e,f=1,2,3,4,5,6

code='''
a <= b and b <= c and c <= d and d <= e and e <= f
'''
total_time_1 = np.mean(
    timeit.repeat(code,globals=globals(),
                  repeat=3, number=1000000))
code='''
a <= b <= c <= d <= e <= f
'''
total_time_2 = np.mean(
    timeit.repeat(code,globals=globals(),

                  repeat=3, number=1000000))
print("time1: ",total_time_1,total_time_2,total_time_1/total_time_2)
