# Check for AIS messages
# If found and not cached then:
# Capture an image. If ship present capture image every second for 60 seconds. Then check. If still present redo.
# If no ship wait 60 seconds and check again. After 5 minutes time out.

# Maximum API usage: An image a minute,
# 1440 images a day or 35000 a month


import socket
import ais.stream
import logging
import json
import sys
import sqlite3
import datetime
import requests
from itushipinfo import itu_identify_vessel
from geofence import Geofence
from capture import Capture

geofence = Geofence()
capture = Capture()
capturesinprogress = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(filename='ais-server.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

conn = sqlite3.connect('ais.db')
c = conn.cursor()

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 10110

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
logging.debug("successful server intiation")

def logais(ais):
    c.execute("INSERT INTO ais VALUES (?, ?)", (datetime.datetime.utcnow().isoformat(), json.dumps(ais)))
    conn.commit()

def logtraffic(ais):
    c.execute('INSERT INTO trafficlog VALUES (?, ?, ?)', (datetime.datetime.utcnow().isoformat(), ais["mmsi"], json.dumps(ais)))
    conn.commit()

def updatevessel(mmsi, ignored, identified, fullinfo):
    if fullinfo == None:
        c.execute('INSERT INTO vesselinfo (mmsi, ignored, identified) VALUES (?, ?, ?)', (mmsi, ignored, identified))
    else:
        c.execute('INSERT INTO vesselinfo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (mmsi, ignored, fullinfo['url'], identified, fullinfo['name'], fullinfo['details'], fullinfo['size'], fullinfo['gross_tonnage'], fullinfo['notes'], fullinfo['flag']))
    conn.commit()

def shouldprocess(ais):
    '''Return list [identified, ignored]'''
    c.execute("SELECT identified, ignored FROM vesselinfo WHERE mmsi = ?", (ais['mmsi'],))
    status = c.fetchone()
    if status == None:
        return [False, False]
    return map(bool, status)

def identifyvessel(ais):
    shipinfo = itu_identify_vessel(ais)
    if shipinfo:
        updatevessel(ais['mmsi'], ignored=False, identified=True, fullinfo=shipinfo)
    else:
        updatevessel(ais['mmsi'], ignored=True, identified=False, fullinfo=None)

def ingeofence(ais):
    if x not in ais or y not in ais: return False
    return geofence(ais.x, ais.y)

while True:

    try:
        data, addr = serverSock.recvfrom(1024)
        payload=data.split(",")

        messagecontainer = ""

        pad = int(payload[-1].split('*')[0][-1])
        msglength = int(payload[1])
        msgpart = int(payload[2])

        if msglength == 1:
            rawmessage = payload[5]
            decodedmessage = ais.decode(rawmessage,pad)
            
            identified, ignored = shouldprocess(decodedmessage)
            logging.info(str(decodedmessage['mmsi']) + " ignored = " + str(ignored))

            if decodedmessage['mmsi'] in capturesinprogress:
                if not ingeofence(decodedmessage):
                    capture.stop(decodedmessage)
                    del capturesinprogress[decodedmessage['mmsi']]
            elif ingeofence(decodedmessage):
                logtraffic(decodedmessage)            
                if not ignored:
                    capture.add(decodedmessage)
                    capturesinprogress[decodedmessage['mmsi']] = True

            if not identified and not ignored:
                identifyvessel(decodedmessage)

            messagecontainer = ""
        
        else: 
            msgcomplete = 0
            messagecontainer += payload[5]
            
            while (msgcomplete == 0): 
                data, addr = serverSock.recvfrom(1024)
                payload=data.split(",")
                rawmessage = payload[5]
                msglength = int(payload[1])
                msgpart = int(payload[2])

                messagecontainer += rawmessage

                logging.debug("incoming data -> %s", str(data))
                logging.debug("message part -> %s", str(msgpart))
                logging.debug("message length -> %s", str(msglength))
                logging.debug("pad ->  %s", str(pad))
                logging.debug("raw message -> %s", str(rawmessage))
                logging.debug("messagecontainer -> %s", str(messagecontainer))

                
                if (msglength == msgpart):
                    pad = int(payload[-1].split('*')[0][-1])
                    
                    #remove escape from test udp
                    messagecontainer = messagecontainer.replace("\\","")

                    logging.debug("final pad ->  %s", str(pad))
                    logging.debug("final messagecontainer -> %s", str(messagecontainer))

                    decodedmessage = ais.decode(messagecontainer,pad)
                    
                    logtraffic(decodedmessage)
                    identified, ignored = shouldprocess(decodedmessage)
                    logging.info(str(decodedmessage['mmsi']) + " ignored = " + str(ignored))
                    if not identified and not ignored:
                        identifyvessel(decodedmessage)
                    elif not ignored:
                        if ingeofence(decodedmessage):
                            # capture
                            pass

                    messagecontainer = ""
                    msgcomplete = 1
    except:
        logging.error(sys.exc_info())


