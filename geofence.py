default_geofence_sydney_harbour = [
(-33.8509936, 151.2108207),
(-33.8536488, 151.2092543),
(-33.8552703, 151.2149835),
(-33.8526152, 151.2159705),
(-33.8509936, 151.2107992),
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
