import os
import psycopg2
database = os.environ['DATABASE']
conn = psycopg2.connect(database)
c = conn.cursor()
c.execute('CREATE TABLE ais (date text, ais text)')
c.execute('CREATE TABLE vesselinfo (mmsi integer PRIMARY KEY, ignored boolean, url text, identified boolean, name text, details text, size text, gross_tonnage text, notes text, flag text, forcecapture boolean)')
c.execute('CREATE TABLE trafficlog (date text, mmsi integer, ais text)')
c.execute('CREATE TABLE captures (date text, mmsi integer, lat integer, lon integer)')
conn.commit()
