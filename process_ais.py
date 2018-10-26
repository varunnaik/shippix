from DB import *
from itushipinfo import itu_identify_vessel
from geofence import Geofence
from capture import Capture
import datetime
import time
import requests
import json
from ais_classifications import classifications

currently_inside_fence = {}
geofence_last_seen = {}
vesseldetails_persist_file = 'vesseldetails.json'

def clean(field):
    return field.strip().replace('@', '')

class Ais_Processor:
    def __init__(self):
        self.geofence = Geofence()
        self.capture = Capture()
        self.capturesinprogress={}
        self.vesseldetails = self.load_vessel_details()
        print "Loaded", len(self.vesseldetails.keys()), "Vessels"

    def ingeofence(self, ais):
        if 'x' not in ais or 'y' not in ais: return False
        return self.geofence.point_in_fence(ais['y'], ais['x'])

    def load_vessel_details(self):
        with open(vesseldetails_persist_file, "r") as json_data:
            try:
                return json.load(json_data)
            except ValueError:
                return {}

    def persist_vessel_details(self):
        with open(vesseldetails_persist_file, "w") as vesseldetails_file:
            json.dump(self.vesseldetails, vesseldetails_file)

    def get_vessel_details(self, mmsi):
        if mmsi not in self.vesseldetails:
            return { "name": "", "details": "", "size": "", "notes": "", "identified": False, "ignored": True }
        return self.vesseldetails[mmsi]

    def process_ais5(self, ais):
        # http://catb.org/gpsd/AIVDM.html#_type_5_static_and_voyage_related_ais
        if ais['id'] != 5:
            raise ValueError('Not an AIS5 message', ais)
        
        dim_b = ais['dim_a']
        dim_s = ais['dim_b']
        dim_p = ais['dim_c']
        dim_sb = ais['dim_d']
        # If too small to photograph we'll ignore it
        ignored = True
        if dim_b + dim_s > 80: # Vessel is > 80m long, excluding ferries, tugs and smaller craft
            ignored = False

        if ais['mmsi'] in self.vesseldetails:
            return

        vesseldetails = {
            'name': clean(ais['name']),
            'flag': '',
            'gross_tonnage': '',
            'url': '',
            'details': classifications[str(ais['type_and_cargo'])],
            'size': str(dim_b+dim_s) + 'm x ' + str(dim_p+dim_sb) + 'm',
            'notes': 'Destination ' + (clean(ais['destination']) or 'Unknown' ) + ', ETA:' + str(ais['eta_day']) + '/' + str(ais['eta_month']),
            'callsign': clean(ais['callsign']),
        }
        vesseldetails['mmsi'] = ais['mmsi']
        vesseldetails['ignored'] = ignored
        vesseldetails['identified'] = True
        self.vesseldetails[ais['mmsi']] = vesseldetails

        print "Update vessel", ais['mmsi'], vesseldetails['name']
        self.persist_vessel_details()

    def process(self, ais):
        mmsi = ais['mmsi']

        vesseldetails = self.get_vessel_details(mmsi)

        identified = vesseldetails['identified']
        ignored = vesseldetails['ignored']
        
        if mmsi in self.capturesinprogress: # If already capturing this vessel
            if not self.ingeofence(ais): # If vessel has left the geofence                
                self.capture.stop(self.capturesinprogress[mmsi])
                images = self.capture.get_images(self.capturesinprogress[mmsi])
                #print "Imagelist to Firebase", images
                #self.update_firebase(currently_inside_fence[mmsi], images)
                del self.capturesinprogress[mmsi]
                del currently_inside_fence[mmsi]
        elif self.ingeofence(ais):            
            now = datetime.datetime.utcnow()            
            if mmsi not in geofence_last_seen:
                geofence_last_seen[mmsi] = now
                return 

            # If this is the second time in 30s that the vessel has reported it's in the geofence then process it
            # This is to prevent logging random jumps in GPS position reported by the ships
            # AIS messages are sent every 2 - 10 seconds when underway so this is a wide margin of error
            # if now - geofence_last_seen[mmsi] > datetime.timedelta(seconds = 30):
            #     print mmsi, vesseldetails['name'], 'ignored: True', now - geofence_last_seen[mmsi]
            #     geofence_last_seen[mmsi] = now # Need two messages in quick succession or we ignore it
            #     return 

            geofence_last_seen[mmsi] = now

            if mmsi not in currently_inside_fence:
                print str(mmsi), vesseldetails['name'], 'ignored:', str(ignored)
                
                currently_inside_fence[mmsi] = {'date': u''+now.isoformat(), 'mmsi': mmsi, 'details': vesseldetails} # Log once only when a ship enters the geofence
            if not ignored:
                print "Attempt capture", mmsi, vesseldetails['name']

                n = datetime.datetime.now()
                captureid = str(mmsi) + str(int(time.time()))
                self.capture.start(captureid, mmsi, vesseldetails)
                self.capturesinprogress[mmsi] = captureid
        else:
            if mmsi in currently_inside_fence: # When a ship leaves the fenced region mark it as outside
                del currently_inside_fence[mmsi]
        # If we have not been able to identify the ship over AIS then attempt to do so against the ITU database           
