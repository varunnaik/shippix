from DB import *
from itushipinfo import itu_identify_vessel
from geofence import Geofence
from capture import Capture
import datetime
import requests
import firebase

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
        return self.geofence.point_in_fence(ais["y"], ais["x"])

    def update_firebase(self, capturedata, imagelist):
    	urls = firebase.upload_images(imagelist)
    	capturedata["urls"] = urls
    	firebase.add_document(capturedata)
    	# TODO: Delete imagelist

    def process(self, ais):
        identified, ignored = shouldprocess(ais)
        #print str(ais["mmsi"]), " ignored:", str(ignored), 'in geofence:', self.ingeofence(ais)

        if ais["mmsi"] in self.capturesinprogress: # If already capturing this vessel
            if not self.ingeofence(ais): # If vessel has left the geofence                
                self.capture.stop(self.capturesinprogress[ais["mmsi"]])
                images = self.capture.get_images(self.capturesinprogress[ais["mmsi"]])
                self.update_firebase(currently_inside_fence[ais["mmsi"]], images)
                del self.capturesinprogress[ais["mmsi"]]
                del currently_inside_fence[ais["mmsi"]]
        elif self.ingeofence(ais):
            if ais["mmsi"] not in currently_inside_fence:
            	print str(ais["mmsi"]), " ignored:", str(ignored)
                logtraffic(ais)
                currently_inside_fence[ais["mmsi"]] = {'date': u''+datetime.datetime.utcnow().isoformat(), 'mmsi': ais['mmsi'], 'ais': ais} # Log once only when a ship enters the geofence
                firebase.add_document(currently_inside_fence[ais["mmsi"]])
            if not ignored:
                n = datetime.datetime.now()
                captureid = str(ais["mmsi"]) + n.strftime("%Y%m%d")
                self.capture.start(captureid)
                self.capturesinprogress[ais["mmsi"]] = captureid
        else:
            if ais["mmsi"] in currently_inside_fence: # When a ship leaves the fenced region mark it as outside
                del currently_inside_fence[ais["mmsi"]]                

        if not identified and not ignored:
            self.identifyvessel(ais) # Note: Synchronous call!