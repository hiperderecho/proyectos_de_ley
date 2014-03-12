#!/usr/bin/env python

# -*- coding: utf-8 -*-
import datetime
import PyRSS2Gen
import config
import dataset
import codecs


def create_rss():
    title = config.title
    link = config.base_url
    description = config.description
    
    
    
    items = []
    
    db = dataset.connect("sqlite:///leyes.db")
    res = db.query("SELECT * FROM proyectos ORDER BY timestamp DESC")
    for i in res:
        titulo = "Proyecto de Ley " + i['numero_proyecto'] + " " + i['titulo'][0:140]
        if len(i['titulo']) > 140:
            titulo += "..."
    
        document_links = "\n\n<br /><br />"
        try:
            document_links += "<a href='" + i['pdf_url'] + "'>PDF</a> "
        except:
            print ""
        document_links += "<a href='" + i['link_to_pdf'] + "'>Expediente</a>"
        this_rss = PyRSS2Gen.RSSItem(
                title = titulo,
                link = "http://" + config.base_url + "p/" + i['short_url'],
                guid = "http://" + config.base_url + "p/" + i['short_url'],
                pubDate = datetime.datetime.fromtimestamp(int(i['timestamp'])),
                description = i['titulo'] + "\n\n<br /><br />Autores: " + i['congresistas'] + document_links,
                )
        items.append(this_rss)
    
    
    rss = PyRSS2Gen.RSS2(
            title = title,
            link = link,
            description = description,
            lastBuildDate = datetime.datetime.now(),
            items = items,
            )
    
    rss.write_xml(codecs.open("rss.xml", "w"))
    

if __name__ == "__main__":
    create_rss()
