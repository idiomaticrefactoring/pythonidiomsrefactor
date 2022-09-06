import timeit

import numpy as np
def sum(a, b):
    return a + b

values = (1, 2)

code = '''
s = sum(values[0],values[1])
'''
total_time_1 = np.mean(
    timeit.repeat(code, globals=globals(),
                  repeat=3, number=10000000))
code = '''
sum(*values)
'''
total_time_2 = np.mean(
    timeit.repeat(code, globals=globals(),

                  repeat=3, number=10000000))
print("time1: ", total_time_1, total_time_2, total_time_1 / total_time_2)

