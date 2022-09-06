import timeit

import numpy as np

n=9
code='''
finishedForLoop = True
for x in range(2, n):
     if n % x == 0:
         # print( n, 'equals', x, '*', n/x)
         finishedForLoop=False
         break
if finishedForLoop:
     pass#print (n, 'is a prime number')
'''
total_time_1 = np.mean(
    timeit.repeat(code,globals=globals(),
                  repeat=3, number=10000000))
code='''
for x in range(2, n):
    if n % x == 0:
        # print (n, 'equals', x, '*', n/x)
        break
else:
    
    #print( n, 'is a prime number')
    pass
'''
total_time_2 = np.mean(
    timeit.repeat(code,globals=globals(),

                  repeat=3, number=10000000))
print("time1: ",total_time_1,total_time_2,total_time_1/total_time_2)
