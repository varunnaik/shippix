import sqlite3
conn = sqlite3.connect('ais.db')
c = conn.cursor()
c.execute('CREATE TABLE ais (date text, ais text)')
c.execute('CREATE TABLE mmsi (mmsi integer PRIMARY KEY, ignored tinyint, name text, details text, size text, gross_tonnage text, notes text, flag text)')
c.execute('CREATE TABLE trafficlog (date text, mmsi integer)')
conn.commit()