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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(filename='ais-server.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

conn = sqlite3.connect('ais.db')
c = conn.cursor()
#c.execute('CREATE TABLE ais (date text, message text)')

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 10110

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
logging.debug("successful server intiation")

def insertdata(data):
	c.execute("INSERT INTO ais VALUES (%s, %s)", (datetime.datetime.utcnow().isoformat(), json.dumps(data)))
	conn.commit()


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

		    logging.info("SUCCESS: decoded message -> %s", str(decodedmessage))
		    print json.dumps(decodedmessage)
		    insertdata(decodedmessage)

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
					
					logging.info("SUCCESS: decoded multipart message -> %s", str(decodedmessage))
					print json.dumps(decodedmessage)
					insertdata(decodedmessage)

					messagecontainer = ""
					msgcomplete = 1

	except:
		logging.warning("failed to process message")
    	

# Note code above implemented a strip of "\" from incoming messages given need to add escape when socat-ing on terminal; should be removed in prod
# Example 2 part message
# echo "\!AIVDM,2,1,9,B,53nFBv01SJ<thHp6220H4heHTf2222222222221?50\:454o<\`9QSlUDp,0*09" | socat - UDP4-DATAGRAM:127.0.0.1:10110 && echo "\!AIVDM,2,2,9,B,888888888888880,2\*2E" | socat - UDP4-DATAGRAM:127.0.0.1:10110
# Example 2 part + 1 part message
#echo "\!AIVDM,2,1,9,B,53nFBv01SJ<thHp6220H4heHTf2222222222221?50\:454o<\`9QSlUDp,0*09" | socat - UDP4-DATAGRAM:127.0.0.1:10110 && echo "\!AIVDM,2,2,9,B,888888888888880,2*2E" | socat - UDP4-DATAGRAM:127.0.0.1:10110 && echo "\!AIVDM,1,1,,B,15MnnEPP0qJe?6dGBV1=2wvF2D4h,0*2AthHp6220H4heHTf2222222222221?50\:454o<\`9QSlUDp,0*09" | socat - UDP4-DATAGRAM:127.0.0.1:10110

#example simple execution of ais.decode
# print ais.decode("53nFBv01SJ<thHp6220H4heHTf2222222222221?50:454o<`9QSlUDp888888888888880",2)

# Note: may need to trim "L" from IMO and MMSI in decoded messages