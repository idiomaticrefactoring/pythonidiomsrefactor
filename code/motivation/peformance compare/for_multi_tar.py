import timeit

import numpy as np
sales = [("Pencil", 0.22, 1500), ("Notebook", 1.30, 550), ("Eraser", 0.75, 1000)]

code = '''
for item in sales:
    a=item[0],item[1],item[2]
'''
total_time_1 = np.mean(
    timeit.repeat(code, globals=globals(),
                  repeat=5, number=1000000))

python_code = '''
for product, price, sold_units in sales:
    a=product,price,sold_units
'''
total_time_2 = np.mean(
    timeit.repeat(python_code, globals=globals(),

                  repeat=5, number=1000000))
print("time1: ", total_time_1, total_time_2, total_time_1 / total_time_2)
