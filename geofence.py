default_geofence_sydney_harbour = [
(-33.8495679, 151.2096190),
(-33.8535775, 151.2081385),
(-33.8563039, 151.2159062),
(-33.8536221, 151.2167859),
(-33.8495679, 151.2096190),
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
