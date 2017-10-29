from DB import *
from itushipinfo import itu_identify_vessel
from geofence import Geofence
from capture import Capture
import datetime
import requests

class Ais_Processor:
    def __init__(self):
        self.geofence = Geofence()
        self.capture = Capture()
        self.capturesinprogress={}
    
    def identifyvessel(self, ais):
        shipinfo = itu_identify_vessel(ais)
        if shipinfo:
            updatevessel(ais['mmsi'], ignored=False, identified=True, fullinfo=shipinfo)
        else:
            updatevessel(ais['mmsi'], ignored=True, identified=False, fullinfo=None)

    def ingeofence(self, ais):
        if x not in ais or y not in ais: return False
        return geofence(ais.x, ais.y)

    def process(self, ais):
        identified, ignored = shouldprocess(ais)
        logging.info(str(ais['mmsi']) + " ignored = " + str(ignored))

        if ais['mmsi'] in self.capturesinprogress:
            if not self.ingeofence(ais):
                logtraffic(ais)
                self.capture.stop(self.capturesinprogress[ais['mmsi']])
                del self.capturesinprogress[ais['mmsi']]
        elif self.ingeofence(ais):
            logtraffic(ais)            
            if not ignored:
            	captureid = str(ais['mmsi']) + n.strftime("%Y%m%d")
                self.capture.add(captureid)
                self.capturesinprogress[ais['mmsi']] = captureid

        if not identified and not ignored:
            self.identifyvessel(ais)