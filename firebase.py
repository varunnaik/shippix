from google.cloud import firestore
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from os.path import basename

cred = credentials.Certificate("/home/pi/shippix/credentials.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'sydneyharbourtraffic.appspot.com'
})
bucket = storage.bucket()

# Project ID is determined by the GCLOUD_PROJECT environment variable
db = firestore.Client()

def add_document(trafficdata):
    doc_ref = db.collection(u'traffic').document(str(trafficdata['mmsi'])+"-"+datetime.datetime.utcnow().strftime("%Y-%m-%d-%H:%M"))
    doc_ref.set(trafficdata)
    print "Uploaded to firebase"

def upload_images(images):
    urls = []
    for image in images:
        blob = bucket.blob(basename(image))
        with open(image, 'rb') as image_file:
            blob.upload_from_file(image_file)
        urls.append(blob.public_url)
    print "Uploaded images to GCS"

    return urls

def sync_shipinfo():
	pass