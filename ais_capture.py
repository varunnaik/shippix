import socket
import ais
from ais import DecodeError
import logging
import json
import sys
from process_ais import Ais_Processor

aisprocessor = Ais_Processor()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 10110

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
logging.debug("server started")

session = {}

while True:

    try:
        data, addr = serverSock.recvfrom(1024)
        payload = data.split(",")

        pad = int(payload[-1].split('*')[0][-1])
        msglength = int(payload[1])
        msgpart = int(payload[2])
        msgseqid = int(payload[3])
        msg = payload[5]

        if msglength == 1:            
            decodedmessage = ais.decode(msg,pad)            
            aisprocessor.process(decodedmessage)
        else:
            if msgpart == 1:
                session[msgseqid] = {}
            session[msgseqid][msgpart] = msg
            print "Add multipart", msgseqid, msgpart, "of", msglength, ":", msg, " :: ", pad
            
            if msglength == msgpart: # Is this the final part?
                msg = ""
                for i in xrange(msgpart):
                    msg += session[msgseqid][i]          
                
                print "Decode multipart", msg, pad, "len", len(msg)
                decodedmessage = ais.decode(msg, 2) # libais rejects AIS5 messages where pad is NOT 2
                print decodedmessage
                aisprocessor.process_ais5(decodedmessage)
    except:
        logging.error(sys.exc_info())


