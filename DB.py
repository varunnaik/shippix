import os
import psycopg2
import datetime
import json

database = os.environ['DATABASE']
conn = psycopg2.connect(database)
c = conn.cursor()

def logais(ais):
    c.execute("INSERT INTO ais VALUES (%s, %s)", (datetime.datetime.utcnow().isoformat(), json.dumps(ais)))
    conn.commit()

def logtraffic(ais):
    c.execute("INSERT INTO trafficlog VALUES (%s, %s, %s)", (datetime.datetime.utcnow().isoformat(), ais["mmsi"], json.dumps(ais)))
    conn.commit()

def getvessel(mmsi):
    c.execute("SELECT name, details, size, notes FROM vesselinfo WHERE mmsi = %s", (mmsi,))
    val = c.fetchone()
    if not val:
        return None
    return {
        'name': val[0],
        'detials': val[1],
        'size': val[2],
        'notes': val[3]
    }

def updatevessel(mmsi, ignored, identified, fullinfo):
    if fullinfo == None:
        c.execute("INSERT INTO vesselinfo (mmsi, ignored, identified) VALUES (%s, %s, %s)  ON CONFLICT (mmsi) DO UPDATE SET ignored = EXCLUDED.ignored", (mmsi, ignored, identified))
    else:
        c.execute("INSERT INTO vesselinfo (mmsi, ignored, url, identified, name, details, size, gross_tonnage, notes, flag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (mmsi) DO UPDATE SET ignored = EXCLUDED.ignored", (mmsi, ignored, fullinfo["url"], identified, fullinfo["name"], fullinfo["details"], fullinfo["size"], fullinfo["gross_tonnage"], fullinfo["notes"], fullinfo["flag"]))
    conn.commit()

def shouldprocess(ais):
    '''Return list [identified, ignored]'''
    c.execute("SELECT identified, ignored, forcecapture FROM vesselinfo WHERE mmsi = %s", (ais["mmsi"],))
    status = c.fetchone()
    if status == None:
        return [False, True] # Ignore all unknown ships
    identified, ignored, forcecapture = status    
    ignored = not forcecapture and ignored == True # Forcecapture trumps ignored - if it is set
    return [identified, ignored]
