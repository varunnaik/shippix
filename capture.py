# If a thread is not already running start one now
# Capture images 
# Terminate

from threading import Timer
timer = None
def start_capture():
	should_capture = True
	timer = Timer(capture, 1)
	timer.start()
	pass

def stop_capture():
	should_capture = False
	timer.cancel()
	pass

def capture():
	if not should_capture:
		return
	# Code to get a picture and save to disk
	timer = Timer(capture, 1)


