#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 StrayWarrior <i@straywarrior.com>
#
from common import *
import math
from scipy.optimize import minimize
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s')

class DimensionError(Exception):
    pass

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
#       the 0-th column: input
#       the 1-st column: output
#   distances: (m x m) matrix
def calculate_factors(balances, distances, method='gravity', method_param={}):
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

# Balance the input-output table
def calculate_distribution(balances, out_weights, try_conver=True):
    # Initial distribution
    distribution = np.zeros(out_weights.shape)
    row_num = len(out_weights)
    for i in range(0, row_num):
        distribution[i] = out_weights[i] * balances[i, 1]

    if not try_conver:
        return distribution
    # Start balance loop:
    balanced = False
    input_errs = np.zeros((1, row_num))
    while (not balanced):
        input_errs_last = np.copy(input_errs)
        # Step 1: Sum all the rows
        for i in range(0, row_num):
            cur_input = np.sum(distribution[:, i])
            real_input = balances[i, 0]
            if (abs(real_input - 0) < 1e-6):
                multiplier = 0
            else:
                multiplier = real_input / cur_input
            distribution[:, i] = distribution[:, i] * multiplier
            input_errs[0, i] = cur_input - real_input

        input_error = np.sum(np.dot(input_errs, input_errs.transpose()))
        if (input_error < 100):
            balanced = True
        else:
            # To avoid infinite loop
            if np.linalg.norm(input_errs - input_errs_last, 2) < 1e-6:
                balanced = True
        # Step 2: Sum all the columns
        for i in range(0, row_num):
            cur_output = np.sum(distribution[i, :])
            real_output = balances[i, 1]
            if (abs(real_output - 0) < 1e-6):
                multiplier = 0
            else:
                multiplier = real_output / cur_output
            distribution[i, :] = distribution[i, :] * multiplier
    return distribution

# Calculate the distribution based on Optimization Method
# Params:
#   x: n x n matrix
#   balances: n x 2 matrix
#   distances: n x n matrix
def optimize_distribution(x, balances, distances):
    # Object: lowest x * r^2 (x is transportation between two points)
    # Restirct: output and input balances
    n = len(x)
    opt_cons = opt_constraints(x, balances)
    opt_bnds = opt_bounds(x)
    r_vec = distances.reshape(1, -1)
    res = minimize(opt_objective_function, x.reshape(1, -1), args=(r_vec, ),
                   method='SLSQP',
                   constraints=opt_cons,
                   options={'maxiter':100, 'disp':True})
    return res

def opt_objective_function(x, arg):
    r = arg[0]
    if (len(x) != len(r)):
        print("opt_objective_function: Error size, x:{0}, " \
              "r:{1}".format(len(x), len(r)))
        raise DimensionError()
    total_cost = sum(x * (r * r))
#    logging.debug('Total cost: %d', total_cost)
    return total_cost

# Generate constraints function
# Because variables are passed in a vector in minimize(), so the index should
# be flatten.
# Params:
#   x: n x n matrix
#   b: n x 2 matrix

class Func:
    def __init__(self, x):
        self.x = x
    def __call__(sel):
        print(self.x)
def opt_constraints(x, b):
    if (len(x) != len(b)):
        logging.error("opt_constraints: Error size")
        raise DimenstionError()
    n = len(x)
    cons = ()
    for i in range(0, n):
        #cons += ({'type': 'eq', 'fun': Func(i)},
        #         {'type': 'eq', 'fun': Func(i)})
        cons += ({'type': 'eq', 'fun': lambda x, i=i, n=n: np.sum(x[i : n * i]) - b[i, 1]},
                 {'type': 'eq', 'fun': lambda x, i=i, n=n: np.sum(x[i : n * n : n]) - b[i, 0]})
        pass
    return cons

def opt_bounds(x):
    n = len(x)
    bounds = ((0, None),) * (n * n)
    return bounds

def main():
    balances = np.genfromtxt('./balances.csv', delimiter=',')
    distances = geoutil.calculate_all_distances(predefined_vars.PROVINCE_POINTS)
    out_weights = calculate_factors(balances, distances)
    np.savetxt('./weights.csv', out_weights, delimiter=",")
    distribution = calculate_distribution(balances, out_weights, False)

    print(optimize_distribution(distribution, balances, distances))

    row_num = len(distribution)
    distribution.resize((row_num + 1), row_num)
    distribution[row_num, :] = np.sum(distribution, axis=0)
    np.savetxt('./transport.csv', distribution, delimiter=",")

if __name__ == '__main__':
    main()
