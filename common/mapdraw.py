# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 StrayWarrior <i@straywarrior.com>
#
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import os

class MapPoint:
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            arg_type = type(args[0])
            if arg_type == int or arg_type == float:
                if len(args) < 2:
                    raise TypeError()
                else:
                    self.lon = args[0]
                    self.lat = args[1]
            elif arg_type == tuple or arg_type == list:
                self.lon = args[0][0]
                self.lat = args[0][1]
        else:
            if 'lon' in kwargs:
                self.lon = kwargs['lon']
            if 'lat' in kwargs:
                self.lat = kwargs['lat']
            if 'coo' in kwargs:
                self.lon = kwargs['coo'][0]
                self.lat = kwargs['coo'][1]
            else:
                raise TypeError()

class ChinaMapDraw:
    def __init__(self):
        self.maphandle = Basemap(llcrnrlon=73., llcrnrlat=18.,
                                 urcrnrlon=136., urcrnrlat=54.,
                                 rsphere=(6378137.00, 6356752.3142),
                                 resolution='h', projection='merc',
                                 lat_0=18.0, lon_0=73.0,
                                 lat_ts=20., fix_aspect=False)
        filedir = os.path.dirname(__file__)
        self.maphandle.readshapefile(shapefile=filedir + '/map/map',
                                     name='china', drawbounds=True,
                                     color='k', linewidth=1, default_encoding='cp1252')

    def draw_greatcircle(self, src, dest, *args, **kwargs):
        self.maphandle.drawgreatcircle(src.lon, src.lat,
                                       dest.lon, dest.lat,
                                       *args, **kwargs)
    
    def draw_point(self, point, *args, **kwargs):
        self.maphandle.plot(point.lon, point.lat, *args, latlon=True, **kwargs)


def drawcircle_between_provinces(maphandle, src=MapPoint(0.0, 0.0),
                                 dest=MapPoint(0.0, 0.0),
                                 linw=2, lincolor='b', linalpha=1.0):
    maphandle.drawgreatcircle(src.lon, src.lat, dest.lon, dest.lat,
                             linewidth=linw, color=lincolor, del_s=50.0,
                             alpha=linalpha)

def drawpoint_on_province(maphandle, dest=MapPoint(0.0, 0.0), *args,
                          **kwargs):
    #maphandle.plot(dest.lon, dest.lat, *args, **kwargs)
    maphandle.plot(dest.lon, dest.lat, *args, latlon=True, **kwargs)

# Draw lines on map
def drawtransport_data(maphandle, transport_data, coordinates, threhold=0,
                       linw_max=3):
    point_num = len(transport_data)

    trans_max = np.max(transport_data)
    trans_min = np.min(transport_data)
    if (trans_min < threhold):
        trans_min = threhold
    trans_delta = trans_max - trans_min

    if (point_num != len(coordinates)):
        print("Point numbers are not equal.")
        return False
    for i in range(0, point_num):
        if (np.sum(transport_data[i, :])):
            drawpoint_on_province(maphandle, coordinates[i], 'go')
        else:
            drawpoint_on_province(maphandle, coordinates[i], 'ro')
    for i in range(0, point_num):
        for j in range(0, point_num):
            if (transport_data[i, j] >= trans_min and i != j):
                factor = (transport_data[i, j] - trans_min) / trans_delta
                drawcircle_between_provinces(maphandle, coordinates[i],
                                             coordinates[j], linalpha=factor,
                                             linw=linw_max * factor)

class PredefinedVars:
    @staticmethod
    def get_province_points(*args):
        beijing  = MapPoint(116.28, 39.54)
        shanghai = MapPoint(121.29, 31.14)
        tianjin  = MapPoint(117.11, 39.09)
        chongqing = MapPoint(106.32, 29.32)
        heilongjiang = MapPoint(126.41, 45.45)
        jilin = MapPoint(123.24, 41.50)
        liaoning = MapPoint(123.25, 41.48)
        neimenggu = MapPoint(111.48, 40.49)
        hebei = MapPoint(114.28, 38.02)
        shanxi1 = MapPoint(112.34, 37.52)
        shandong = MapPoint(117, 36.38)
        henan = MapPoint(113.42, 34.48)
        shanxi3 = MapPoint(108.54, 34.16)
        gansu = MapPoint(103.49, 36.03)
        ningxia = MapPoint(106.16, 38.20)
        qinghai = MapPoint(101.45, 36.38)
        xinjiang = MapPoint(87.36, 43.48)
        anhui = MapPoint(117.18, 31.51)
        jiangsu = MapPoint(118.50, 32.02)
        zhejiang = MapPoint(120.09, 30.14)
        hunan = MapPoint(113, 28.11)
        jiangxi = MapPoint(115.52, 28.41)
        hubei = MapPoint(114.21, 30.37)
        sichuan = MapPoint(104.05, 30.39)
        guizhou = MapPoint(106.42, 26.35)
        fujian = MapPoint(119.18, 26.05)
        taiwan = MapPoint(121.31, 25.03)
        guangdong = MapPoint(113.15, 23.08)
        hainan = MapPoint(110.20, 20.02)
        guangxi = MapPoint(108.20, 22.48)
        yunnan = MapPoint(102.41, 25)
        xizang = MapPoint(90.08, 29.39)
        xianggang = MapPoint(114.10, 22.18)
        aomen = MapPoint(113.35, 22.14)

        province_points = (beijing, tianjin, hebei, shanxi1, neimenggu, liaoning, jilin,
                           heilongjiang, shanghai, jiangsu, zhejiang, anhui, fujian, jiangxi,
                           shandong, henan, hubei, hunan, guangdong, guangxi, hainan,
                           chongqing, sichuan, guizhou, yunnan, shanxi3, gansu, qinghai,
                           ningxia, xinjiang)
        if len(args) < 1:
            return province_points
        else:
            return province_points[args[0]]


def main():
    from predefined_vars import PROVINCE_POINTS
    fig=plt.figure()
    ax=fig.add_axes([0.1,0.1,0.8,0.8])
    # setup mercator map projection.
    m = Basemap(llcrnrlon=73.,llcrnrlat=18.,urcrnrlon=136.,urcrnrlat=54.,
                rsphere=(6378137.00,6356752.3142),
                resolution='h',projection='merc',
                lat_0=18.,lon_0=73.,lat_ts=20.,
                fix_aspect=False)
    m.readshapefile(shapefile='./map/map', name='china', drawbounds=True,
                    color='k', linewidth=1, default_encoding='cp1252')
    transport_data = np.genfromtxt('../transport.csv', delimiter=",")

    drawtransport_data(m, transport_data, PROVINCE_POINTS)
    plt.show()

if __name__ == '__main__':
    main()
