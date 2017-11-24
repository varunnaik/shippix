import sqlite3
conn = sqlite3.connect('ais.db')
c = conn.cursor()
c.execute('CREATE TABLE ais (date text, ais text)')
c.execute('CREATE TABLE vesselinfo (mmsi integer PRIMARY KEY, ignored tinyint, url text, identified tinyint, name text, details text, size text, gross_tonnage text, notes text, flag tex, forcecapture tinyint)')
c.execute('CREATE TABLE trafficlog (date text, mmsi integer, ais text)')
c.execute('CREATE TABLE captures (date text, mmsi integer, lat integer, lon integer)')
conn.commit()