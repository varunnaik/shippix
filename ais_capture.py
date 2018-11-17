import socket
import ais
from ais import DecodeError
import logging
import json
import sys
from process_ais import Ais_Processor
import traceback

aisprocessor = Ais_Processor()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 10110

def connect():
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
    print("Connected to AIS server")
    return serverSock

serverSock = connect()
print "AIS listener started" 
session = {}

def getmessage():
    global serverSock
    data, addr = serverSock.recvfrom(1024)

    payload = data.split(",")

    pad = int(payload[-1].split('*')[0][-1])
    msglength = int(payload[1])
    msgpart = int(payload[2])
    msgseqid = 0
    if payload[3]:
        msgseqid = int(payload[3])
    msg = payload[5]
    return (msg, pad, msgpart, msglength, msgseqid)

while True:

    try:
        
        msg, pad, msgpart, msglength, msgseqid = getmessage()
        if msglength == 1:            
            decodedmessage = ais.decode(msg,pad)            
            aisprocessor.process(decodedmessage)
        else:
            while msglength != msgpart:
                msgfragment, pad, msgpart, msglength, msgseqid = getmessage()
                msg += msgfragment
                
                if msglength == msgpart: # Is this the final part?
                    decodedmessage = ais.decode(msg[0:71], 2) # libais rejects AIS5 messages where pad is NOT 2 and length is NOT 71
                    aisprocessor.process_ais5(decodedmessage)
    except DecodeError:
        pass
    except:
        logging.error(traceback.format_exc())


