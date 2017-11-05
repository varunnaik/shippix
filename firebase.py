import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("/home/pi/shippix/credentials.json")
firebase_admin.initialize_app(cred)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sydneyharbourtraffic.firebaseio.com'
})

ref = db.reference('server/saving-data/fireblog')



from google.cloud import firestore
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate("/home/pi/shippix/credentials.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'sydneyharbourtraffic.appspot.com'
})
bucket = storage.bucket()

# Project ID is determined by the GCLOUD_PROJECT environment variable
db = firestore.Client()

def add_document(trafficdata):
    doc_ref = db.collection(u'traffic').document(str(trafficdata['mmsi'])+datetime.datetime.utcnow().strftime("%Y-%m-%d-%H:%m"))
    doc_ref.set(trafficdata)

def upload_images([images]):
    urls = []
    for image in images:
        blob = bucket.blob(image)
        with open(image, 'rb') as image_file:
            blob.upload_from_file(image_file)
        urls.append(blob.public_url)

    return urls