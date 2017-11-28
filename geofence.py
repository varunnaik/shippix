default_geofence_sydney_harbour = [
(-33.8502807, 151.2114000),
(-33.8535597, 151.2090826),
(-33.8562326, 151.2145329),
(-33.8546556, 151.2146616),
(-33.8502807, 151.2114000),
]


class Geofence:
    def __init__(self, geofence=default_geofence_sydney_harbour):
        self.poly = geofence

    def point_in_fence(self, x, y):
        verticeCount = len(self.poly)
        i = 0
        j = verticeCount - 1
        inside = False

        for i in range(verticeCount):
                if  ((self.poly[i][1] > y) != (self.poly[j][1] > y)) and \
                        (x < (self.poly[j][0] - self.poly[i][0]) * (y - self.poly[i][1]) / (self.poly[j][1] - self.poly[i][1]) + self.poly[i][0]):
                    inside = not inside
                j = i
        return inside
