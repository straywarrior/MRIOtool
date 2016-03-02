import geopy.distance as geodis

# Calculate great_circle distance between two points on earth
# x and y should have member 'lat' and 'lon'
# For example, x and y can be instances of class ProvincePoint
# Return:
#   double: distance in kilometers.
def calculate_distance(x, y, type='km'):
    dis = geodis.great_circle((x.lat, x.lon), (y.lat, y.lon))
    return dis.km

def calculate_all_distances(point_list, out_filename=''):
    result = []
    for x in point_list:
        distance = []
        for y in point_list:
            distance.append(geodis.great_circle((x.lat, x.lon),
                                                (y.lat, y.lon)).km)
        result.append(distance)

    if out_filename:
        with open(out_filename, 'w', newline='') as result_file:
            result_writer = csv.writer(result_file, delimiter=',', dialect='excel')
            for line in result:
                result_writer.writerow(line)

    return result

def main():
    from common.predefined_vars import PROVINCE_POINTS

    res = calculate_all_distances(PROVINCE_POINTS)
    print(res)

if __name__ == '__main__':
    main()
