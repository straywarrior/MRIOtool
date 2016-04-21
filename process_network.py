#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 StrayWarrior <i@straywarrior.com>
#

import csv
import io
from common import *
from common.mapdraw import MapPoint

def getall_lon_lat_data(filename):
    all_lon_lat_data = []
    with open(filename) as china_lon_lat_file:
        lonlat_reader = csv.reader(china_lon_lat_file, delimiter='\t')
        for line in lonlat_reader:
            all_lon_lat_data.append(line)
    return all_lon_lat_data

def search_lon_lat(name, database):
    for line in database:
        if name in line[2]:
            return (float(line[3]), float(line[4]))

def getall_network_lines(filename):
    all_lon_lat_data = getall_lon_lat_data('China_LonAndLat.txt')
    all_lines = []
    with open(filename) as network_line_file:
        line_reader = csv.reader(network_line_file, delimiter=',')
        for line in line_reader:
            all_lines.append((search_lon_lat(line[0], all_lon_lat_data),
                              search_lon_lat(line[1], all_lon_lat_data)))
    return all_lines

def draw_all_lines(lines):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    m = mapdraw.ChinaMapDraw()
    for line in lines:
        if line[0] and line[1]:
            m.draw_greatcircle(MapPoint(line[0]), MapPoint(line[1]), color='b')
            m.draw_point(MapPoint(line[0]), marker='o', markersize='3',
                         color='g')
            m.draw_point(MapPoint(line[1]), marker='o', markersize='3',
                         color='g')
        else:
            print("Warning: invalid coordinate")
    plt.show()

def main():
    all_lines = getall_network_lines('network_lines.txt')
    draw_all_lines(all_lines)

if __name__ == '__main__':
    main()
