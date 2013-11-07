#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os.path
import glob
import subprocess
import re
import codecs
import sys
import json
import string
from scrape import parse_names
from pyatom import AtomFeed
import datetime

def prettify(item):
    out = ""
    out += "\n<div>\n"
    out += "<p><b>" + item['numero_proyecto'] + "</b>\n"
    out += "<h4>" + item['titulo'] +  "</h4>\n"
    out += "<p>" + parse_names(item['congresistas']) + "</p>\n"

    out += "</div>\n"
    return out

def pre(texto):
    out = "<pre>"
    out += texto
    out += "</pre>"
    return out

def generate_html(texto, item):
    f = codecs.open("base.html", "r", "utf-8")
    base_html = f.read()
    f.close()

    f = codecs.open("proyectos_data.json", "r", "utf-8")
    data = json.loads(f.read())
    f.close()

    html = string.replace(base_html, "{% content %}", pre(texto))
    title = re.sub("pdf/", "", item)
    title = title.replace("_", "/")
    title = title.replace(".pdf", "")
    html = string.replace(html, "{% title %}", title)

    for i in data:
        if i['numero_proyecto'] == title:
            titulo = prettify(i)

    html = string.replace(html, "{% titulo %}", titulo)

    html_file = re.sub(".pdf", ".html", item)
    f = codecs.open(html_file, "w", "utf-8")
    f.write(html)
    f.close()

# search for PDFs in folder
if os.path.isdir("pdf"):
    lista = glob.glob(os.path.join("pdf", "*pdf"))
    if len(lista) > 0:
        for item in lista:
            # check if corresponding html exists
            if os.path.isfile(item.replace(".pdf", ".html")):
                print "* done %s already" % item
                continue
            else:
                # extract images
                cmd = "pdfimages " + item + " " + item
                p = subprocess.check_call(cmd, shell=True)

                # do OCR
                images = glob.glob(item + '*p?m')
                #print images
                for image in images:
                    cmd = "tesseract " + image + " " + re.sub("\.[a-z]{3}$", "", image)
                    cmd += " -l spa"
                    p = subprocess.check_call(cmd, shell=True)

                # put everything together in one html file
                txts = glob.glob(item + '*txt')
                txts.sort()
                texto = ""
                for txt in txts:
                    f = codecs.open(txt, "r", "utf-8")
                    texto += f.read()
                    f.close()
                outfile = re.sub(".pdf$", ".txt", item)
                f = codecs.open(outfile, "w", "utf-8")
                f.write(texto)
                f.close()
                generate_html(texto, item)

                # clean up
                rm_files = glob.glob(item + "*p?m")
                for i in rm_files:
                    os.remove(i)
                rm_files = glob.glob(item + "*txt")
                for i in rm_files:
                    os.remove(i)

# create RSS feed
feed = AtomFeed(title="Proyectos de Ley",
                subtitle=u'del Congreso de la República del Perú',
                feed_url = "http://myurl.com/feed",
                url = "http://myurl.com",
                author = "Me")

html_files = glob.glob(os.path.join("pdf", "*html"))
data_file = codecs.open("proyectos_data.json", "r", "utf-8")
data = json.loads(data_file.read())
data_file.close()

for i in html_files:
    title = i.replace("pdf/", "")
    title = title.replace(".html", "")
    title = title.replace("_", "/")
    for json in data:
        if json['numero_proyecto'] == title:
            content = json['titulo'] + "<br />"
            content += "autores: " + json['congresistas']
    feed.add(title = title,
            content = content,
            content_type = "html",
            author = "Me",
            url = "http://myurl.com/" + i,
            updated=datetime.datetime.utcnow())

f = codecs.open("feed.xml", "w", "utf-8")
f.write(feed.to_string())
f.close()
