#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 StrayWarrior <i@straywarrior.com>
#
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

class ProvincePoint:
    lon = 0.0
    lat = 0.0
    def __init__(self, lon = 0.0, lat = 0.0):
        self.lon = lon
        self.lat = lat

def drawcircle_between_provinces(maphanle, src=ProvincePoint(0.0, 0.0),
                                 dest=ProvincePoint(0.0, 0.0),
                                 linw=2, lincolor='b', linalpha=1.0):
    maphanle.drawgreatcircle(src.lon, src.lat, dest.lon, dest.lat,
                             linewidth=linw, color=lincolor, del_s=50.0,
                             alpha=linalpha)

def drawpoint_on_province(maphandle, dest=ProvincePoint(0.0, 0.0), *args,
                          **kwargs):
    #maphandle.plot(dest.lon, dest.lat, *args, **kwargs)
    maphandle.plot(dest.lon, dest.lat, *args, latlon=True, **kwargs)
