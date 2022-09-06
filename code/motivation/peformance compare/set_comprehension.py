import timeit
import numpy as np
simpsons = "Homer Simpson is son of Abraham Simpson and Father of Bart Simpson"
chars = simpsons.split()
code='''
simpsons_set =set()
for word in chars:
    simpsons_set.add(word)
'''
total_time_1 = np.mean(
    timeit.repeat(code,globals=globals(),
                  repeat=3, number=1000000))
code='''
simpsons_set = {word for word in chars}
'''
total_time_2 = np.mean(
    timeit.repeat(code,globals=globals(),

                  repeat=3, number=1000000))
print("time1: ",total_time_1,total_time_2,total_time_1/total_time_2)