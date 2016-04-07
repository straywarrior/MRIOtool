#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 StrayWarrior <i@straywarrior.com>
#
from common import *
import csv
import math
from scipy.optimize import linprog 
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s')

class DimensionError(Exception):
    pass


def calculate_comprehensive_factor(distances, unit_costs):
    if distances.size != unit_costs.size:
        raise DimensionError()
    # If there is a zero, then it's not valid distance
    # The related var should be set to 0
    # In fact, 0x3f3f3f3f is a penalty that can ensure a variable to be 0
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

def gen_objective_function_str(c):
    res = "min="
    for i in range(0, len(c)):
        res += "x{}*{:f}+".format(i, c[i])
    res += "0;"
    return res


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
    return cons

def gen_eq_constraints_mat(b, btype='total'):
    n = len(b)
    if btype == 'total':
        mat_A = np.zeros((2 * n, n * n), dtype=np.int)
        for i in range(0, n):
            # input balance for group i
            mat_A[i * 2, i : n * n : n] = 1
            # onput balance for group i
            mat_A[i * 2 + 1, i * n : (i + 1) * n] = 1
        mat_b = b.reshape(2 * n, 1)
    elif btype == 'net':
        mat_A = np.zeros((n, n * n), dtype=np.int)
        for i in range(0, n):
            # net = input - output
            mat_A[i, i : n * n : n] = 1
            mat_A[i, i * n : (i + 1) * n] = -1
        mat_b = b.reshape(n, 1)
    else:
        raise Exception()
    return {'A' : mat_A, 'b' : mat_b}

def gen_ub_constraints_mat(s, d):
    n = len(s)
    if n != len(d):
        raise DimensionError()
    mat_A = np.zeros((2 * n, n * n), dtype=np.float64)
    for i in range(0, n):
        # total output should be less than total production
        mat_A[i * 2, i * n : (i + 1) * n] = 1
        # total input should be less than total consumption
        mat_A[i * 2 + 1, i : n * n : n] = 1
    mat_b = np.concatenate((s, d), 1).reshape(2 * n, 1)
    return {'A' : mat_A, 'b' : mat_b}


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

def read_cost_fromtxt(filename, n=0):
    unit_costs = [None] * n
    PRICE_WATER = 0.03
    PRICE_RAIL  = 0.16
    PRICE_ROAD  = 0.5

    with open(filename) as cost_file:
        cost_reader = csv.reader(cost_file, delimiter=',')
        i = 0
        for cost_row in cost_reader:
            unit_costs[i] = np.array(cost_row, np.float64)
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
    return unit_costs

def main():
    POINT_NUM = 30
    VAR_NUM = POINT_NUM ** 2

    balances = np.genfromtxt('balances.csv', delimiter=',')

#    supply_and_demand = np.genfromtxt('csj_supply_and_demand.csv', delimiter=',')

    skip_line = 2
    # Pre-process the distance file
    with open('nation_network.csv', 'r') as network_file:
        network_reader = csv.reader(network_file, delimiter=',')
        i = 0
        distance_file = open('nation_distance.csv', 'w')
        distance_writer = csv.writer(distance_file, delimiter=',')
        cost_file = open('nation_cost.csv', 'w')
        cost_writer = csv.writer(cost_file, delimiter=',')

        for row in network_reader:
            i += 1
            if (i >= skip_line):
                row_to_write = []
                for j in range(4, len(row), 3):
                    if row[j] == '':
                        break
                    row_to_write.append(row[j])
                distance_writer.writerow(row_to_write)

                row_to_write = []
                for j in range(5, len(row), 3):
                    if row[j] == '':
                        break
                    row_to_write.append(row[j])
                cost_writer.writerow(row_to_write)

        distance_file.close()
        cost_file.close()

    distances = [None] * VAR_NUM
    with open('nation_distance.csv') as distance_file:
        distance_reader = csv.reader(distance_file, delimiter=',')
        i = 0
        for distance_row in distance_reader:
            distances[i] = np.array(distance_row, np.float64)
            i += 1

    unit_costs = read_cost_fromtxt('nation_cost.csv', VAR_NUM)

    comprehensive_factors = np.zeros(VAR_NUM, dtype=np.float64)
    for i in range(0, VAR_NUM):
        comprehensive_factors[i] = calculate_comprehensive_factor(distances[i],
                                                                  unit_costs[i])
    np.savetxt('comprehensive_factors.csv', comprehensive_factors, delimiter=',')
    #zero_var_list = [0, 1, 2, 5, 10, 15]
    """
    zero_cons = gen_zero_constraints(zero_var_list)
    balance_cons = gen_constraints(balances)
    opt_cons = zero_cons + balance_cons

    zero_bounds = gen_gt_zero_bounds(VAR_NUM)

    opt_fun_str = gen_objective_function_str(comprehensive_factors)
    print(opt_fun_str)
    print(gen_constraints_str(balances))
    print(gen_zero_constraints_str(zero_var_list))

    """

#    comprehensive_factors = comprehensive_factors.reshape(-1, 16)

    opt_eq = gen_eq_constraints_mat(balances, 'total')
    opt_A_eq = opt_eq['A']
    opt_b_eq = opt_eq['b']
    """
    supply = supply_and_demand[:, [0]]
    demand = supply_and_demand[:, [1]]
    opt_ub = gen_ub_constraints_mat(supply, demand)
    opt_A_ub = opt_ub['A']
    opt_b_ub = opt_ub['b']
    """

    opt_result = linprog(comprehensive_factors,
                         A_eq=opt_A_eq,
                         b_eq=opt_b_eq)
    #print(opt_result)
    np.savetxt('opt_result.csv', opt_result.x.reshape(POINT_NUM, POINT_NUM),
               delimiter=',')
    

if __name__ == '__main__':
    main()
