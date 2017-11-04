# Capture images one per second for 60 seconds.
# Can have multiple captures running simultaneously
#import picamera
from threading import Timer
import datetime
# https://www.raspberrypi.org/documentation/usage/camera/python/README.md

class Capture:
    def __init__(self):
        #self.camera = picamera.PiCamera()
        self.activecaptures = {}

    def start(self, code, captureSeconds=60):
        '''Given an arbitrary code, captures images with that codename till told to stop'''
        if code in self.activecaptures:
        	return False

        self.activecaptures[code] = { 'capture': True, 'end': datetime.datetime.now() + datetime.timedelta(seconds = captureSeconds), 'seq': 0 }
        # Note: All captures will have the same code...
        if not self.timer:
            self.timer = Timer(self.capture_image, 1, [code])
            self.timer.start()
        self.capture_image(code)

    def capture_image(self, code):
    	'''Capture an image provided the capture has not been stopped'''
        if not self.activecaptures[code]['capture'] \
                or self.activecaptures[code]['end'] <= datetime.datetime.now(): # If this capture is finished
            del self.activecaptures[code] # Then delete the capture
            if len(self.activecaptures) == 0: # If this was the last active capture
                self.timer.cancel()    # Then also delete the timer itself
                self.timer = None
        else:
            self.activecaptures[code]['seq'] += 1;
            #self.camera.capture("%s_%s.jpg", (code, self.activecaptures[code]['seq']))

    def stop(self, code):
    	'''Stop capture'''
        if code in self.activecaptures:
            self.activecaptures[code] = False
 



