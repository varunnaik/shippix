default_geofence_sydney_harbour = [
(-33.8493897,151.2084603),
(-33.8529182,151.2064862),   
(-33.8561613,151.2154985),   
(-33.8533191,151.2163782),
(-33.8493897,151.2084603),
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
