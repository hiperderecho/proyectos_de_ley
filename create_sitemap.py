#!/usr/bin/env python

# -*- coding: utf-8 -*-
from apesmit import Sitemap
import config
import codecs
import dataset
import datetime
import glob
import os




def create_sitemap():
    sm = Sitemap(changefreq="daily")
    sm.add("http://" + config.base_url, lastmod="today")
    
    
    db = dataset.connect("sqlite:///leyes.db")
    res = db.query("SELECT * FROM proyectos ORDER BY timestamp DESC")
    for i in res:
        url = "http://" + config.base_url + "p/" + i['short_url']
        lastmod = str(datetime.datetime.fromtimestamp(int(i['timestamp'])))
        lastmod = lastmod.split(" ")[0]
        sm.add(url, lastmod=lastmod)


    for i in glob.glob(os.path.join(config.base_folder, "congresista/*")):
        i = os.path.basename(i)
        url = "http://" + config.base_url + "congresista/" + i + "/index.html"
        sm.add(url, lastmod="today")
    
    
    out = codecs.open("sitemap.xml", "w", "utf-8")
    sm.write(out)
    out.close()
    

if __name__ == "__main__":
    create_sitemap()
