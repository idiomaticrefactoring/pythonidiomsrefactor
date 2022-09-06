import timeit

import numpy as np

if __name__ == '__main__':
    code = '''
a = 2
b = 3
c = 5
d = 7
    '''
    total_time_1 = np.min(
        timeit.repeat(code,
                      repeat=3, number=100000000))
    code = '''
a, b, c, d = 2, 3, 5, 7
    '''
    total_time_2 = np.min(
        timeit.repeat(code,

                      repeat=3, number=100000000))
    print("time1: ", total_time_1, total_time_2, total_time_1 / total_time_2)
