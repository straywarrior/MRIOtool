from common import *
from common.mapdraw import *
from common.predefined_vars import *
import random

def distort_line_points(points, mode='up'):
    #distort_factor = random.randrange(1, 100) / 500
    distort_factor = 0.05
    n = len(points[0])
    m = n / 2
    if mode == 'up':
        for i in range(1, n - 1):
            real_factor = (1 - abs(i - m) / m) * distort_factor + 1
            #points[0][i] *= real_factor
            points[1][i] *= real_factor
    else:
        for i in range(1, n - 1):
            real_factor = (1 - abs(i - m) / m) * distort_factor + 1
            #points[0][i] /= real_factor
            points[1][i] /= real_factor
    return points

def draw_gradient_line(maphandle, lon1, lat1, lon2, lat2, *args, point_num=500,
                       distort_mode='up', **kwargs):
    points = maphandle.gcpoints(lon1, lat1, lon2, lat2, point_num)
    print(points[0][5])
    points = distort_line_points(points, distort_mode)
    print(points[0][5])
    maphandle.plot(points[0], points[1], 'b-')
    """
    for i in range(0, point_num):
        #real_alpha = 0.7 + i * 0.3 / point_num
        real_alpha = 1
        real_size = 1.5 + i * 2.5 / point_num
        maphandle.plot(points[0][i], points[1][i], 'b.', *args,
                       alpha=real_alpha, ms=real_size, **kwargs)

    """

def draw_gradient_line_between_province(maphandle, p1, p2, *args, **kwargs):
    draw_gradient_line(maphandle, p1.lon, p1.lat, p2.lon, p2.lat, *args,
                       **kwargs)


# read data
trans_data = np.genfromtxt('./opt_result.csv', delimiter=',')
trans_max = np.max(trans_data)
trans_min = trans_max
for i in range(0, 30):
    for j in range(0, 30):
        cur = trans_data[i, j]
        if ( np.abs(cur - 0) > 1e-6 and cur < trans_min ):
            trans_min = cur
trans_del = trans_max - trans_min
linwidth_max = 3

# create new figure, axes instances.
fig=plt.figure()
ax=fig.add_axes([0.1,0.1,0.8,0.8])
# setup mercator map projection.
m = Basemap(llcrnrlon=73.,llcrnrlat=18.,urcrnrlon=136.,urcrnrlat=54.,
                        rsphere=(6378137.00,6356752.3142),
                        resolution='h',projection='merc',
                        lat_0=18.,lon_0=73.,lat_ts=20., fix_aspect=False)
for i in range(0, 30):
    if (np.sum(trans_data[i, :])):
        drawpoint_on_province(m, predefined_vars.PROVINCE_POINTS[i], 'go')
    else:
        drawpoint_on_province(m, predefined_vars.PROVINCE_POINTS[i], 'ro')

# draw Province-to-Province data
for i in range(0, 30):
    for j in range(0, 30):
        if (trans_data[i, j] >= trans_min and i != j):
            if j > i:
                dismode = 'down'
            else:
                dismode = 'up'
            #factor = (trans_data[i, j] - trans_min) / trans_del * 0.8 + 0.2
            draw_gradient_line_between_province(m,
                                                PROVINCE_POINTS[i],
                                                PROVINCE_POINTS[j],
                                                point_num = 500,
                                                distort_mode = dismode)
            '''
            drawcircle_between_provinces(m, predefined_vars.PROVINCE_POINTS[i], 
                                         predefined_vars.PROVINCE_POINTS[j],
                                         linw=linwidth_max * factor,
                                         linalpha=factor)
            ''' 

m.readshapefile(shapefile='./common/map/map',
                name='china', drawbounds=True, color='k', linewidth=1, default_encoding='cp1252')
# draw parallels
# m.drawparallels(np.arange(10,90,20),labels=[1,1,0,1])
# draw meridians
# m.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1])
plt.show()
