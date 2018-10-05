default_geofence_sydney_harbour = [
(-33.8495679,151.2096190),
(-33.8511272,151.2075806),
(-33.8521385,151.2064111),
(-33.8530897,151.2063200),
(-33.8532211,151.2072587),
(-33.8539473,151.2094796),
(-33.8561101,151.2107403),
(-33.8576671,151.2126446),
(-33.8567494,151.2173868),
(-33.8535330,151.2183952),
(-33.8495679,151.2096190)
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
