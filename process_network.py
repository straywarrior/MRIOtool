#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 StrayWarrior <i@straywarrior.com>
#

import csv
import io
import sys
import time
from multiprocessing import Pool, TimeoutError
from common import *
from common.mapdraw import MapPoint

class Timer:
    def __init__(self):
        self.last_time = time.clock()
    
    def tick(self, message="Timer"):
        this_time = time.clock()
        real_time = this_time - self.last_time
        self.last_time = this_time
        print("[{0}]{1} s.".format(message, real_time))


def getall_lon_lat_data(filename):
    all_lon_lat_data = []
    with open(filename, encoding='utf-8') as china_lon_lat_file:
        lonlat_reader = csv.reader(china_lon_lat_file, delimiter='\t')
        for line in lonlat_reader:
            all_lon_lat_data.append(line)
    return all_lon_lat_data

def search_lon_lat(name, database):
    for line in database:
        if name in line[2]:
            return (float(line[3]), float(line[4]))

def process_line(line, database):
    return ((search_lon_lat(line[0], database),
             search_lon_lat(line[1], database),
             line[2]))

def getall_network_lines(filename):
    all_lon_lat_data = getall_lon_lat_data('data/China_LonAndLat.txt')
    all_lines = []
    with open(filename, encoding='utf-8') as network_line_file:
        line_reader = csv.reader(network_line_file, delimiter=',')
        with Pool(processes=16) as pool:
            async_res = [pool.apply_async(process_line, (line, all_lon_lat_data)) for line in line_reader]
            all_lines.extend([res.get() for res in async_res])
    return all_lines

def draw_line(m, line):
    if line[0] and line[1]:
        line_colors = {'1': 'b', '2': 'g', '3': 'r'}
        m.draw_greatcircle(MapPoint(line[0]), MapPoint(line[1]), color=line_colors[line[2]])
        #m.draw_random_arc(MapPoint(line[0]), MapPoint(line[1]), color=line_colors[line[2]])
        m.draw_point(MapPoint(line[0]), marker='o', markersize='2',
                     color='r')
        m.draw_point(MapPoint(line[1]), marker='o', markersize='2',
                     color='g')
    else:
        print("Warning: invalid coordinate")

def draw_all_lines(lines):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    timer = Timer()
    m = mapdraw.ChinaMapDraw()
    timer.tick("Init Map")
    for line in lines:
        draw_line(m, line)
    plt.savefig("nation_network.png", dpi=300)

def main():
    timer = Timer()
    all_lines = getall_network_lines(sys.argv[1])
    timer.tick("Search")
    draw_all_lines(all_lines)
    timer.tick("Paint")

if __name__ == '__main__':
    main()
