# Capture images one per second for 60 seconds.
# Can have multiple captures running simultaneously
import picamera
from threading import Timer
import datetime
# https://www.raspberrypi.org/documentation/usage/camera/python/README.md

class Capture:
    def __init__(self):
        self.camera = picamera.PiCamera()
		cam.rotation=90
		cam.resolution=(3280, 2464)#(1809, 1017)
		cam.sharpness=85
		cam.zoom = (0.27, 0.41, 0.51, 0.55)
		cam.capture('test.jpg', resize=(1027,600), thumbnail=None)
        self.activecaptures = {}
        self.captureimages = {}


    def start(self, code, captureSeconds=30):
        '''Given an arbitrary code, captures images with that codename till told to stop'''
        if code in self.activecaptures:
        	return False
        print "Start capture"
        self.captureimages[code] = []
        self.activecaptures[code] = { 'capture': True, 'end': datetime.datetime.now() + datetime.timedelta(seconds = captureSeconds), 'seq': 0, 'timer': None }
        self.activecaptures[code]['timer'] = Timer(3, self.capture_image, [code])
        self.activecaptures[code]['timer'].start()
        self.capture_image(code)

    def capture_image(self, code):
    	'''Capture an image provided the capture has not been stopped'''
        if not self.activecaptures[code]['capture'] \
                or self.activecaptures[code]['end'] <= datetime.datetime.now(): # If this capture is finished
            self.activecaptures[code]['timer'].cancel()    
            del self.activecaptures[code] # Then delete the capture
        else:
            self.activecaptures[code]['seq'] += 1;
            filename = "img/%s_%s.jpg" % (code, self.activecaptures[code]['seq'])
            self.camera.capture(filename, resize=(1548, 470))
            self.captureimages[code].append(filename)
            self.activecaptures[code]['timer'] = Timer(3, self.capture_image, [code])
            self.activecaptures[code]['timer'].start()
            print "Capture", self.activecaptures[code]['seq']

    def stop(self, code):
    	'''Stop capture'''
        if code in self.activecaptures:
            self.activecaptures[code] = False

    def get_images(self, code):
    	if code in self.captureimages:
    		return self.captureimages[code]
    	else:
    		return None
 
 	def delete_images(self, code):
 		# TODO: Delete images on disk and free up disk space
 		pass



