# Capture images one per second for 60 seconds.
# Can have multiple captures running simultaneously
import picamera
import io
import boto3
from threading import Timer
import datetime
import time
import os
import json
import botocore.config
# https://www.raspberrypi.org/documentation/usage/camera/python/README.md
cfg = botocore.config.Config(retries={"max_attempts": 0})
s3 = boto3.resource("s3")
client = boto3.client("lambda", config=cfg)
capture_file = "captures.json"
capture_file_path = "/var/tmpfs/"
lambdaarn = os.environ["LAMBDAARN"]

class Capture:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.rotation=270
        self.camera.resolution=(1920,1080)# Max = (3280, 2464)
        self.camera.sharpness=50#-100 to +100, 0 = default
        self.camera.zoom = (0.149, 0.162, 0.728, 0.803)
        self.activecaptures = {}
        self.captureimages = {}
        self.resize = (1089,434)
        self.camera.start_preview() #Warm the camera up
        self.bucket_name = os.environ["BUCKET"]
        self.last_capture = {"filename": "", "time": None}
        # Download captures file and cache locally
        s3.Object(self.bucket_name, capture_file).download_file(capture_file_path + capture_file)

    def get_last_capture(self):
        return self.last_capture

    def start(self, code, mmsi, details, captureSeconds=230):
        '''Given an arbitrary code, captures images with that codename till told to stop'''
        if code in self.activecaptures:
            print "Already capturing!"
            return False
        print "Start capture"
        self.captureimages[code] = []
        self.activecaptures[code] = { "capture": True, "end": datetime.datetime.now() + datetime.timedelta(seconds = captureSeconds), "seq": 0, "timer": None, "mmsi": mmsi, "details": details }
        self.capture_image(code)

    def capture_image(self, code):
        '''Capture an image provided the capture has not been stopped'''
        if (self.activecaptures[code] and not self.activecaptures[code]["capture"]) \
                or self.activecaptures[code]["end"] <= datetime.datetime.now(): # If this capture is finished
            print "Capture finished"
            self.activecaptures[code]["timer"].cancel()    
            cleanuptimer = Timer(15, self.capture_cleanup, [code])# Delay to ensure files finish uploading
            cleanuptimer.start()
        else:
            self.activecaptures[code]["seq"] += 1
            filename = "%s_%04d.jpg" % (code, self.activecaptures[code]["seq"])
            self.capture_s3("img/"+filename)
            self.captureimages[code].append(filename)
            self.activecaptures[code]["timer"] = Timer(1, self.capture_image, [code])
            self.activecaptures[code]["timer"].start()
            print "Capture", code, ":", self.activecaptures[code]["seq"]

    def capture_cleanup(self, code):
        # Process images to video
        print "Invoke lambda"
        self.store_capture(code, self.activecaptures[code]["mmsi"], self.activecaptures[code]["details"])
        del self.activecaptures[code] # Then delete the capture
        client.invoke(FunctionName=lambdaarn,
                         InvocationType="Event",
                         Payload=json.dumps({"filelist": self.captureimages[code], "outfilename": str(code) + ".mp4"}))

    def reprocess_capture(self, code):
        if code in self.captureimages:
            client.invoke(FunctionName=lambdaarn,
                         InvocationType="Event",
                         Payload=json.dumps({"filelist": self.captureimages[code], "outfilename": str(code) + ".mp4"}))

    def store_snapshot(self):
        capture_s3(self, snapshot)
        return self.last_capture

    def capture_s3(self, filename):
        '''Capture image with camera and upload to s3 using given filename'''
        # Create the in-memory stream
        stream = io.BytesIO()
        self.camera.capture(stream, format="jpeg", resize=self.resize)
        # "Rewind" the stream to the beginning so we can read its content
        stream.seek(0)
        s3.Object(self.bucket_name, filename).put(Body=stream) #.upload_fileobj(stream)
        stream.close()
        self.last_capture["filename"] = filename
        self.last_capture["time"] = int(time.time())

    def capture_file(self, filename):
        self.camera.capture(filename, resize=self.resize)

    def stop(self, code):
        '''Stop capture'''
        if code in self.activecaptures:
            print "Capture aborted!"
            self.activecaptures[code]["capture"] = False

    def get_images(self, code):
        if code in self.captureimages:
            return self.captureimages[code]
        else:
            return None

    def store_capture(self, code, mmsi, details):
        with open(capture_file_path + capture_file, "r+") as json_data:
            d = json.load(json_data)
            if (details["specialcapture"]):
                d["specialcaptures"].append({"code": code, "details": "details"})
            else:
                d["captures"].append(code)
                if mmsi not in d["info"] and details["name"]:
                    d["info"][mmsi] = {"name": details["name"], "description": details["details"], "size": details["size"]}
            json_data.seek(0)
            json.dump(d, json_data)
            json_data.truncate()
        s3.Object(self.bucket_name, capture_file).upload_file(capture_file_path + capture_file, ExtraArgs={"ACL":"public-read"})

# Enhancements: Use the RPI capture instead of timer
# If after dark increase exposure
