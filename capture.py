# If a thread is not already running start one now
# Capture images 
# Terminate
import picamera
from threading import Timer

# https://www.raspberrypi.org/documentation/usage/camera/python/README.md

class Capture:
	def __init__(self):
		self.camera = picamera.PiCamera()
		self.activecaptures = {}

	def start(code):
		if code in self.captures: return False
		self.activecaptures[code] = True
		if not self.timer:
			self.timer = Timer(self.capture_image, 1, [code])
			self.timer.start()
		self.capture_image(code)

	def capture_image(code):
		if not self.activecaptures[code]: # If this capture is finished
			del self.activecaptures[code] # Then delete the capture
			if len(self.activecaptures) == 0: # If this was the last active capture
				self.timer.cancel()	# Then also delete the timer itself
				self.timer = None
		else:
			camera.capture(code + ".jpg")

	def stop(code):
		if code in self.activecaptures:
			self.activecaptures[code] = False
 



