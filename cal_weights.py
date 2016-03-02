#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 StrayWarrior <i@straywarrior.com>
#
#import common
from common import *
import math

# Gravity Model
# F = G * m1^p1 * m2^p2 / r^pr
# Return:
#   F: double
def gravity_function(m1, m2, r, G=1, p1=1, p2=1, pr=2):
    F = G * math.pow(m1, p1) * math.pow(m2, p2) / math.pow(r, pr)
    return F

# Normalize a vector
# if twopass is True, will ignore the elements smaller than threhold
def norm_vector(vec, twopass=False, threhold=0):
    # Normalize: Step 1
    vec_sum = np.sum(vec)
    if not (vec_sum > 0):
        return
    # Note: Only use this type of operator can modify vec in place
    vec /= vec_sum
    # Normalize: Step 2
    if not twopass:
        return
    for i in range(0, len(vec)):
        if vec[i] < threhold:
            vec[i] = 0
    vec_sum = np.sum(vec)
    vec /= vec_sum
    return

# Read total inputs and total outputs
# And read or calculate distance between the two points
# Then calculate the factors
# Params:
#   balances:  (m x 2) matrix
#   distances: (m x m) matrix
def calculate_factors(balances, distances):
    point_num = len(balances)
    if (point_num != len(distances)):
        print("Point numbers are not equal.")
        return False
    out_weights = np.zeros((point_num, point_num))
    for i in range(0, point_num):
        # positive output
        if (balances[i][1] > 0):
            for j in range(0, point_num):
                # j doesn't have input 
                if (i == j or not(balances[j][0] > 0)):
                    continue
                distance = distances[i][j]
                out_weights[i][j] = gravity_function(balances[i][1],
                                                     balances[j][0], distance,
                                                     pr=4)
        norm_vector(out_weights[i], twopass=True, threhold=1e-2)

    return out_weights

def main():
    balances = np.genfromtxt('./balances.csv', delimiter=',')
    distances = geoutil.calculate_all_distances(predefined_vars.PROVINCE_POINTS)
    result = calculate_factors(balances, distances)
    np.savetxt('./weights.csv', result, delimiter=",")

if __name__ == '__main__':
    main()
