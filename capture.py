# Capture images one per second for 60 seconds.
# Can have multiple captures running simultaneously
import picamera
import io
import boto3
from threading import Timer
import datetime
import os
import json
# https://www.raspberrypi.org/documentation/usage/camera/python/README.md
s3 = boto3.resource('s3')
client = boto3.client('lambda')

lambdaarn = 'arn:aws:lambda:ap-southeast-2:807832556430:function:imagesToVideo'


class Capture:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.rotation=270
        self.camera.resolution=(3280, 2464)#(1809, 1017)
        self.camera.sharpness=45
        self.camera.zoom = (0.10714285714285714, 0.29024390243902437, 0.2792207792207792, 0.526219512195122)
        self.activecaptures = {}
        self.captureimages = {}
        self.resize = (1089,434)
        self.camera.start_preview() #Warm the camera up
        self.bucket_name = os.environ['BUCKET']


    def start(self, code, captureSeconds=90):
        '''Given an arbitrary code, captures images with that codename till told to stop'''
        if code in self.activecaptures:
            print "Already capturing!"
            return False
        print "Start capture"
        self.captureimages[code] = []
        self.activecaptures[code] = { 'capture': True, 'end': datetime.datetime.now() + datetime.timedelta(seconds = captureSeconds), 'seq': 0, 'timer': None }
        self.capture_image(code)

    def capture_image(self, code):
        '''Capture an image provided the capture has not been stopped'''
        if (self.activecaptures[code] and not self.activecaptures[code]['capture']) \
                or self.activecaptures[code]['end'] <= datetime.datetime.now(): # If this capture is finished
            print "Capture finished"
            self.activecaptures[code]['timer'].cancel()    
            cleanuptimer = Timer(5, self.capture_cleanup, str(code))# Delay to ensure files finish uploading
            cleanuptimer.start()
        else:
            self.activecaptures[code]['seq'] += 1;
            filename = "img/%s_%03d.jpg" % (code, self.activecaptures[code]['seq'])
            self.capture_s3(filename)
            self.captureimages[code].append(filename)
            self.activecaptures[code]['timer'] = Timer(1, self.capture_image, str(code))
            self.activecaptures[code]['timer'].start()
            print "Capture", code, ":", self.%[code]['seq']

    def capture_cleanup(self, code):
        # Process images to video
        client.invoke(FunctionName=lambdaarn,
                         InvocationType='RequestResponse',
                         Payload=json.dumps({"filelist": self.captureimages[code], "outfilename": str(code) + ".avi"}))
        del self.activecaptures[code] # Then delete the capture

    def capture_s3(self, filename):
        '''Capture image with camera and upload to s3 using given filename'''
        # Create the in-memory stream
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg', resize=self.resize)
        # "Rewind" the stream to the beginning so we can read its content
        stream.seek(0)
        s3.Object(self.bucket_name, filename).put(Body=stream) #.upload_fileobj(stream)
        stream.close()

    def capture_file(self, filename):
        self.camera.capture(filename, resize=self.resize)

    def stop(self, code):
        '''Stop capture'''
        if code in self.activecaptures:
            print "Capture aborted!"
            self.activecaptures[code]['capture'] = False

    def get_images(self, code):
        if code in self.captureimages:
            return self.captureimages[code]
        else:
            return None
 
    def delete_images(self, code):
         # TODO: Delete images on disk and free up disk space
         pass


# Enhancements: Use the RPI capture instead of timer
# If after dark increase exposure
