#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 StrayWarrior <i@straywarrior.com>
#
from common import *
import csv
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

# Calculate the possibility of transportation betwwen two province
# Use comprehensive distance and price information.
# Then return the average cost and one-direction output distance

def calculate_comprehensive_factor(distances, unit_costs):
    if distances.size != unit_costs.size:
        raise DimensionError()
    # If there is a zero, then it's not valid distance
    # The related var should be set to 0
    if distances[0] == 0:
        return 0x3f3f3f3f
    cost_per_unit = distances * unit_costs
    probability = 1 / cost_per_unit
    # normalize probability
    probability /= np.sum(probability)
    average_distance = np.sum(distances * probability)
    average_cost = np.sum(unit_costs * probability)
    #ret = {'average_distance' : average_distance,
    #       'average_cost' : average_cost}
    ret = average_distance * average_cost
    return ret

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
#   costs    : n x n matrix
def optimize_distribution(x, balances, distances, costs=1):
    # Object: lowest x * r^2 (x is transportation between two points)
    # Restirct: output and input balances
    n = len(x)
    opt_cons = gen_constraints(balances)
    opt_bnds = gen_bounds(x)
    r_vec = distances.reshape(1, -1)
    res = minimize(opt_objective_function, x.reshape(1, -1), args=(r_vec, ),
                   method='SLSQP',
                   constraints=opt_cons,
                   options={'maxiter':100, 'disp':True})
    return res

def opt_objective_function(x, arg):
    c = arg[0]
    if (len(x) != len(c)):
        print("opt_objective_function: Error size, x:{0}, " \
              "r:{1}".format(len(x), len(c)))
        raise DimensionError()
    total_cost = sum(x * c)
    logging.debug('Total cost: %d', total_cost)
    return total_cost

# Generate constraints function
# Because variables are passed in a vector in minimize(), so the index should
# be flatten.
# Params:
#   b: n x 2 matrix

# Constraints:
#   Every province's total input and output should be balanced
#   No in-Province transportation, that is x_ii = 0
def gen_constraints(b):
    n = len(b)
    cons = ()
    for i in range(0, n):
        cons += ({'type': 'eq', # Output balance
                  'fun': lambda x, i=i, n=n: np.sum(x[n * i : n * (i + 1)]) - b[i, 1]},
                 {'type': 'eq', # Input balance
                  'fun': lambda x, i=i, n=n: np.sum(x[i : n * n : n]) - b[i, 0]},
                 {'type': 'eq',
                  'fun': lambda x, i=i, n=n: x[i + i * n]}
                 )
        pass
    return cons

def gen_constraints_str(b):
    n = len(b)
    res = ""
    for i in range(0, n):
        cur_cons = ""
        for j in range(n * i, n * (i + 1)):
            cur_cons += "x{}+".format(j)
        cur_cons += "0={:f};\n".format(b[i, 1])
        res += cur_cons

        cur_cons = ""
        for j in range(i, n * n, n):
            cur_cons += "x{}+".format(j)
        cur_cons += "0={:f};\n".format(b[i, 0])
        res += cur_cons
    return res

class ZeroConstraint:
    def __init__(self, _index):
        self.index = _index
    def __call__(self, x):
        return x[self.index]


# Specify the vars that should be zero
# accept a list
# return a tuple
def gen_zero_constraints(index, dim_2=0, dim_3=0):
    cons = ()
    real_index = 0
    for i in index:
        if type(i) == int:
            real_index = i
        elif type(i) == tuple:
            real_index = i[1] + i[0] * dim_2
        cons += ({'type': 'eq', 'fun': ZeroConstraint(real_index)}, )
    return cons

def gen_zero_constraints_str(index, dim_2=0, dim_3=0):
    res = ""
    real_index = 0
    for i in index:
        if type(i) == int:
            real_index = i
        elif type(i) == tuple:
            real_index = i[1] + i[0] * dim_2
        res += "x{}=0;\n".format(real_index)
    return res

# Backport
def gen_bounds(x):
    n = len(x)
    return gen_gt_zero_bounds(n * n)

def gen_gt_zero_bounds(n):
    bounds = ((0, None),) * n
    return bounds

def main():
    '''
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
    '''

    balances = np.array([
                        [365.4202, 0],
                        [2411.9378, 100],
                        [1281.6206, 100],
                        [0, 4246.5823]
                        ])

    distances = [None] * 16

    with open('csj_distance.csv') as csj_distance_file:
        distance_reader = csv.reader(csj_distance_file, delimiter=',')
        i = 0
        for distance_row in distance_reader:
            distances[i] = np.array(distance_row, np.float64)
            i += 1

    unit_costs = [None] * 16
    PRICE_WATER = 0.03
    PRICE_RAIL  = 0.16
    PRICE_ROAD  = 0.5

    with open('csj_cost.csv') as csj_cost_file:
        cost_reader = csv.reader(csj_cost_file, delimiter=',')
        i = 0
        for cost_row in cost_reader:
            unit_costs[i] = np.zeros(distances[i].shape)
            for j in range(0, len(cost_row)):
                v = cost_row[j]
                if v == '0':
                    pass
                if v == '1':
                    unit_costs[i][j] = PRICE_WATER
                if v == '2':
                    unit_costs[i][j] = PRICE_RAIL
                if v == '3':
                    unit_costs[i][j] = PRICE_ROAD
            i += 1

    comprehensive_factors = np.zeros(16, dtype=np.float64)
    for i in range(0, 16):
        comprehensive_factors[i] = calculate_comprehensive_factor(distances[i],
                                                                  unit_costs[i])
    zero_var_list = [0, 1, 2, 5, 10, 15]
    zero_cons = gen_zero_constraints(zero_var_list)
    balance_cons = gen_constraints(balances)
    opt_cons = zero_cons + balance_cons

    zero_bounds = gen_gt_zero_bounds(16)

    opt_fun_str = ""
    for i in range(0, 16):
        opt_fun_str += "x{}*{:f}+".format(i, comprehensive_factors[i])
    print(opt_fun_str)
    print(gen_constraints_str(balances))
    print(gen_zero_constraints_str(zero_var_list))

    x0 = np.zeros((1,16))
    comprehensive_factors = comprehensive_factors.reshape(1, 16)
    res = minimize(opt_objective_function, x0,
                   args=(comprehensive_factors, ),
                   method='SLSQP',
                   constraints=balance_cons,
                   bounds=zero_bounds,
                   options={'maxiter':100, 'disp':True})

if __name__ == '__main__':
    main()
