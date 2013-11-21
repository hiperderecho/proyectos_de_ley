#!/usr/bin/env python

import json
import cgi
import cgitb
import dataset
import sys
import scrape
cgitb.enable()

data = cgi.FieldStorage()


if 'get' in data and data['get'].value == "number_of_pages":
    db = dataset.connect("sqlite:///leyes.db")
    table = db['proyectos']
    rows = table.all()
    i = 0
    for row in rows:
        i += 1
    result = {"number_of_pages": i}
    
    print "Content-Type: application/json\n"
    print json.dumps(result)
elif 'start' in data:
    start = data['start'].value
    end = data['end'].value

    db = dataset.connect("sqlite:///leyes.db")
    # We will limit to show only 20 results per page
    query = "SELECT * FROM proyectos ORDER BY codigo DESC LIMIT %s OFFSET %s" % (20, start)
    res = db.query(query)
    out = ""
    for i in res:
        out += scrape.prettify(i)
    print "Content-Type: application/json\n"
    print json.dumps({"output": out})
elif 'search' in data:
    keyword = data['search'].value

    db = dataset.connect("sqlite:///leyes.db")
    query = "SELECT titulo, pdf_url, link_to_pdf FROM proyectos WHERE "
    query += "titulo like '%" + keyword + "%' ORDER BY codigo DESC" 
    res = db.query(query)
    out = []
    for i in res:
        out.append(i)
    print "Content-Type: application/json\n"
    print json.dumps(out)

else:
    pass
