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
    for i in range(0, point_num):
        # positive output
        if (balances[i][1] > 0):
            for j in range(0, point_num):
                # j doesn't have input 
                if (i == j or not(balances[j][0] > 0)):
                    continue
                distance = distances[i][j]

    pass

def main():
    balances = np.genfromtxt('./balances.csv', delimiter=',')
    distances = geoutil.calculate_all_distances(predefined_vars.PROVINCE_POINTS)
    calculate_factors(balances, distances)

if __name__ == '__main__':
    main()
