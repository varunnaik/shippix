import socket
import ais.stream
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
            
            aisprocessor.process(decodedmessage)

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
                    
                    aisprocessor.process(decodedmessage)

                    messagecontainer = ""
                    msgcomplete = 1
    except:
        logging.error(sys.exc_info())


