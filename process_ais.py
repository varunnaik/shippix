from DB import *
from itushipinfo import itu_identify_vessel
from geofence import Geofence
from capture import Capture
import datetime
import requests

currently_inside_fence = {}

class Ais_Processor:
    def __init__(self):
        self.geofence = Geofence()
        self.capture = Capture()
        self.capturesinprogress={}
    
    def identifyvessel(self, ais):
        shipinfo = itu_identify_vessel(ais)
        if shipinfo:
            updatevessel(ais["mmsi"], ignored=False, identified=True, fullinfo=shipinfo)
        else:
            updatevessel(ais["mmsi"], ignored=True, identified=False, fullinfo=None)

    def ingeofence(self, ais):
        if "x" not in ais or "y" not in ais: return False
        return self.geofence.pointInFence(ais["y"], ais["x"])

    def process(self, ais):
        identified, ignored = shouldprocess(ais)
        print str(ais["mmsi"]), " ignored:", str(ignored), 'in geofence:', self.ingeofence(ais)

        if ais["mmsi"] in self.capturesinprogress: # If already capturing this vessel
            if not self.ingeofence(ais): # If vessel has left the geofence                
                self.capture.stop(self.capturesinprogress[ais["mmsi"]])
                del self.capturesinprogress[ais["mmsi"]]
        elif self.ingeofence(ais):
            if ais["mmsi"] not in currently_inside_fence:
                logtraffic(ais)
                currently_inside_fence[ais["mmsi"]] = True # Log once only when a ship enters the geofence
            if not ignored:
                captureid = str(ais["mmsi"]) + n.strftime("%Y%m%d")
                self.capture.add(captureid)
                self.capturesinprogress[ais["mmsi"]] = captureid
        else:
            if ais["mmsi"] in currently_inside_fence: # When a ship leaves the fenced region mark it as outside
                del currently_inside_fence[ais["mmsi"]]

        if not identified and not ignored:
            self.identifyvessel(ais) # Note: Synchronous call!