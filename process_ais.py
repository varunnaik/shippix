from DB import *
from itushipinfo import itu_identify_vessel
from geofence import Geofence
from capture import Capture
import datetime
import requests
import firebase
from ais_classifications import classifications

currently_inside_fence = {}
geofence_last_seen = {}

def clean(field):
    field.strip().replace('@', '')

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
        if 'x' not in ais or 'y' not in ais: return False
        return self.geofence.point_in_fence(ais['y'], ais['x'])

    def update_firebase(self, capturedata, imagelist):
        urls = firebase.upload_images(imagelist)
        capturedata['urls'] = urls
        firebase.add_capture(capturedata)
        # TODO: Delete imagelist

    def process_ais5(ais):
        # http://catb.org/gpsd/AIVDM.html#_type_5_static_and_voyage_related_ais
        if ais['id'] != 5:
            throw("Not an AIS 5 message")
        
        dim_b = ais['dim_a']
        dim_s = ais['dim_b']
        dim_p = ais['dim_c']
        dim_sb = ais['dim_d']
        # If too small to photograph we'll ignore it
        ignored = True
        if dim_b + dim_s > 80: # Vessel is > 80m long, excluding ferries, tugs and smaller craft
            ignored = False

        shipinfo = {
            'name': clean(ais['name']),
            'flag': '',
            'gross_tonnage': '',
            'url': '',
            'details': classifications[str(ais['type_and_cargo'])],
            'size': str(dim_b+dim_s) + 'm x' + str(dim_p+dim_sb) + 'm',
            'notes': 'Destination ' + clean(ais['destination']) + ', ETA:' + str(ais['eta_day']) + '/' + str(ais['eta_month']),
            'callsign': clean(ais['callsign'])
        }

        updatevessel(ais['mmsi'], ignored=ignored, identified=True, fullinfo=shipinfo)

    def process(self, ais):
        identified, ignored = shouldprocess(ais)
        mmsi = ais['mmsi']
        if mmsi in self.capturesinprogress: # If already capturing this vessel
            if not self.ingeofence(ais): # If vessel has left the geofence                
                self.capture.stop(self.capturesinprogress[mmsi])
                images = self.capture.get_images(self.capturesinprogress[mmsi])
                self.update_firebase(currently_inside_fence[mmsi], images)
                del self.capturesinprogress[mmsi]
                del currently_inside_fence[mmsi]
        elif self.ingeofence(ais):            
            now = datetime.datetime.utcnow()            
            if mmsi not in geofence_last_seen:
                geofence_last_seen[mmsi] = now
                return 

            # if this is the second time in 30s that we've seen this vessel in the geofence then process it
            if geofence_last_seen[mmsi] + datetime.timedelta(seconds = 30) > now:
                geofence_last_seen[mmsi] = now # Need two messages in quick succession or we ignore it
                return 

            geofence_last_seen[mmsi] = now

            if mmsi not in currently_inside_fence:
                print str(mmsi), ' ignored:', str(ignored)
                logtraffic(ais)
                currently_inside_fence[mmsi] = {'date': u''+now.isoformat(), 'mmsi': mmsi} # Log once only when a ship enters the geofence
                firebase.add_document(currently_inside_fence[mmsi])
            if not ignored:
                n = datetime.datetime.now()
                captureid = str(mmsi) + n.strftime('%Y%m%d')
                self.capture.start(captureid)
                self.capturesinprogress[mmsi] = captureid
        else:
            if mmsi in currently_inside_fence: # When a ship leaves the fenced region mark it as outside
                del currently_inside_fence[mmsi]                

        #if not identified and not ignored:
        #    self.identifyvessel(ais) # Note: Synchronous call!