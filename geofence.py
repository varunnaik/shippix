default_geofence_sydney_harbour = [
(-33.8505302, 151.2107563),
(-33.8534527, 151.2085247),
(-33.8563751, 151.2167645),
(-33.8529538, 151.2180519),
(-33.8505302, 151.2107563)
]

class Geofence:
    def __init__(self, geofence=default_geofence_sydney_harbour):
        self.poly = geofence

    def pointInFence(self, x, y):
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
