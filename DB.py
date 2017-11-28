import sqlite3
import datetime
import json

conn = sqlite3.connect("ais.db")
c = conn.cursor()

def logais(ais):
    c.execute("INSERT INTO ais VALUES (?, ?)", (datetime.datetime.utcnow().isoformat(), json.dumps(ais)))
    conn.commit()

def logtraffic(ais):
    c.execute("INSERT INTO trafficlog VALUES (?, ?, ?)", (datetime.datetime.utcnow().isoformat(), ais["mmsi"], json.dumps(ais)))
    conn.commit()

def getvessel(mmsi):
    c.execute("SELECT name, details, size, notes FROM vesselinfo WHERE mmsi = ?", (mmsi,))
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
        c.execute("INSERT OR REPLACE INTO vesselinfo (mmsi, ignored, identified) VALUES (?, ?, ?)", (mmsi, ignored, identified))
    else:
        c.execute("INSERT OR REPLACE INTO vesselinfo (mmsi, ignored, url, identified, name, details, size, gross_tonnage, notes, flag) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (mmsi, ignored, fullinfo["url"], identified, fullinfo["name"], fullinfo["details"], fullinfo["size"], fullinfo["gross_tonnage"], fullinfo["notes"], fullinfo["flag"]))
    conn.commit()

def shouldprocess(ais):
    '''Return list [identified, ignored]'''
    c.execute("SELECT identified, ignored, forcecapture FROM vesselinfo WHERE mmsi = ?", (ais["mmsi"],))
    status = c.fetchone()
    if status == None:
        return [False, True] # Ignore all unknown ships
    identified, ignored, forcecapture = status    
    ignored = not forcecapture and ignored == 1 # Forcecapture trumps ignored - if it is set
    return [identified, ignored]
