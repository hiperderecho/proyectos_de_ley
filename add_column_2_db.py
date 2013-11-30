#!/usr/bin/env python

import dataset
import sqlalchemy
import short_url
import sys
import time
import datetime


"""
Update our database with new data fields

* 2013-11-30  short_url
* 2013-11-30  unix timestamp
"""

db = dataset.connect("sqlite:///leyes.db")
table = db['proyectos']


res = db.query("SELECT * from proyectos")

data = []
for i in res:
    if "fecha_presentacion" in i:
        if i['fecha_presentacion'] != None:
            s = i['fecha_presentacion']
            try:
                timestamp = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
            except:
                s = "01/01/2013"
                timestamp = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
        else:
            s = "01/01/2013"
            timestamp = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())

    dic = {"id": i['id'], "timestamp":timestamp}
    data.append(dic)



for i in data:
    j = {}
    j['timestamp'] = i['timestamp']
    j['id'] = i['id']
    table.upsert(j, ['id'])
sys.exit()
