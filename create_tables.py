import sqlite3
conn = sqlite3.connect('ais.db')
c = conn.cursor()
c.execute('CREATE TABLE ais (date text, message text)')
c.execute('CREATE TABLE mmsi (mmsi text, ignored tinyint)')
c.execute('CREATE INDEX mmsi_index ON mmsi (mmsi)')
conn.commit()