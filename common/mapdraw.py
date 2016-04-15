# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 StrayWarrior <i@straywarrior.com>
#
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

class ProvincePoint:
    def __init__(self, lon = 0.0, lat = 0.0):
        self.lon = lon
        self.lat = lat

def drawcircle_between_provinces(maphandle, src=ProvincePoint(0.0, 0.0),
                                 dest=ProvincePoint(0.0, 0.0),
                                 linw=2, lincolor='b', linalpha=1.0):
    maphandle.drawgreatcircle(src.lon, src.lat, dest.lon, dest.lat,
                             linewidth=linw, color=lincolor, del_s=50.0,
                             alpha=linalpha)

def drawpoint_on_province(maphandle, dest=ProvincePoint(0.0, 0.0), *args,
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
