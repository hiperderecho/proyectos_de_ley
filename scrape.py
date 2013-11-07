#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import socks
import cookielib
import socket
from bs4 import BeautifulSoup
import requests
import sys
import re
from os import listdir
import codecs
import urllib2
import time
import random
import string
import os.path

random.seed();  
tor = False
debug = False

if tor:
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('Accept-Charset', 'utf-8')]


def parse_names(string):
    """ 
    Parse string of names.
    """
    names = ""
    for i in string.split(","):
        i = re.sub("\s{2}", ", ", i)
        names += i + "; "
    names = re.sub(";\s$", "", names)
    return names

def generate_html():
    f = codecs.open("base.html", "r", "utf-8")
    base_html = f.read()
    f.close()

    f = codecs.open("proyectos_data.json", "r", "utf-8")
    data = json.loads(f.read())
    f.close()

    html = string.replace(base_html, "{% content %}", prettify(data))

    f = codecs.open("proyectos_de_ley.html", "w", "utf-8")
    f.write(html)
    f.close()

def prettify(data):
    out = ""
    for item in data:
        out += "\n<div>\n"
        out += "<p><b>" + item['numero_proyecto'] + "</b>\n"
        out += "<h4>" + item['titulo'] +  "</h4>\n"
        out += "<p>" + parse_names(item['congresistas']) + "</p>\n"

        if 'pdf_url' in item:
            out += "<a class='btn btn-lg btn-primary'"
            out += " href='" + item['pdf_url'] + "' role='button'>PDF</a>"
        else:
            out += "<a class='btn btn-lg btn-primary disabled'"
            out += " href='#' role='button'>Sin PDF</a>"

        if 'link_to_pdf' in item:
            out += " <a class='btn btn-lg btn-primary'"
            out += " href='" + item['link_to_pdf'] + "' role='button'>EXPEDIENTE</a>"
        else:
            out += " <a class='btn btn-lg btn-primary disabled'"
            out += " href='#' role='button'>Sin EXPEDIENTE</a>"
        out += "</div>\n"
        out += "<hr>\n"
    return out
        

def extract_pdf_url(link):
    #link = "http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/02787?opendocument"
    try:
        pdf_soup = get(link)
        for i in pdf_soup.find_all("a"):
            if i['href'].endswith('pdf'):
                return i['href']
    except:
        # Algunos proyectos de ley no tienen link hacia PDFs
        return "none"


def extract_metadata(dic):
    if debug:
        #f = open("fibri.html", "r")
        f = open("PAporNumeroInverso.html", "r")
        html_doc = f.read()
        f.close()
        project_soup = BeautifulSoup(html_doc)
    else:
        project_soup = get(dic['link'])

    metadata = {}
    metadata['titulo'] = dic['titulo']
    print "* titulo: %s" % metadata['titulo']
    for item in project_soup.find_all("input"):
        if item['name'] == "CodIni_web_1":
            metadata['numero_proyecto'] = item['value']
            print "* numero_proyecto: %s" % metadata['numero_proyecto']
        #if item['name'] == "DesGrupParla":
            #metadata['grupo_parlamentario'] = item['value']
        #if item['name'] == "NombreDeLaComision":
            #metadata['comision'] = item['value']
        if item['name'] == "NomCongre":
            metadata['congresistas'] = item['value']
            print "* congresistas: %s" % metadata['congresistas']
        if item['name'] == "CodIni":
            metadata['codigo'] = item['value']
            print "* codigo: %s" % metadata['codigo']
        if item['name'] == "fechapre":
            metadata['fecha_presentacion'] = item['value']
            print "* fecha_presentacion: %s" % metadata['fecha_presentacion']
    link_to_pdf = 'http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/'
    link_to_pdf += metadata['codigo'] + '?opendocument'
    metadata['link_to_pdf'] = link_to_pdf
    metadata['pdf_url'] = extract_pdf_url(link_to_pdf)

    # Algunos proyectos de Ley no tienen links hacia PDFs
    if metadata['pdf_url'] == "none":
        del metadata['pdf_url']
        del metadata['link_to_pdf']
    print metadata
    return metadata

def extract_doc_links(soup):
    our_links = []
    for link in soup.find_all("a"):
        if re.search("[0-9]{5}/[0-9]{4}", link.get_text()):
            href = link.get("href")
            title = link.get("title")
            if href.endswith("ocument"):
                our_link = "http://www2.congreso.gob.pe" + "/" + href
                our_link = re.sub("//Sicr","/Sirc", our_link)
                our_links.append({'link': our_link, 'titulo':title})
    return our_links

def processed_links():
    processed_links = []
    # Returns a list of links found in our data file "proyectos_data.json"
    if os.path.isfile("proyectos_data.json"):
        f = codecs.open("proyectos_data.json", "r", "utf-8")
        try: 
            data = json.loads(f.read());
        except:
            return processed_links
    else:
        return processed_links


    if data == "empty":
        return processed_links
    else:
        for item in data:
            processed_links.append(item['link'])

    return processed_links


def get(url):
    n = random.random()*5;  
    #time.sleep(n);  
    #print "* sleep for %f" % n
    request = urllib2.Request(url)
    request.add_header('Cache-Control','max-age=0')
    response = opener.open(request)
    soup = BeautifulSoup(response.read().decode("utf-8"))
    return soup

# save proyecto data into file
def save_project(metadata):
    if os.path.isfile("proyectos_data.json"):
        f = codecs.open("proyectos_data.json", "r", "utf-8")
        data = f.read()
        if len(data) < 2:
            file_empty = True
        else:
            file_empty = False

    else:
        file_empty = True

    if file_empty == True:
        data = []
        data.append(metadata)
        f = codecs.open("proyectos_data.json", "w", "utf-8")
        f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
        f.close()
    else:
        f = codecs.open("proyectos_data.json", "r", "utf-8")
        data = json.loads(f.read())
        f.close()
        data.append(metadata)
        f = codecs.open("proyectos_data.json", "w", "utf-8")
        f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
        f.close()



## ------------------------------------------------
def main():
    url = "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/PAporNumeroInverso?OpenView"
    soup = get(url)
    links = extract_doc_links(soup)

    for item in links:
        link = item['link']
        if link not in processed_links():
            print "* getting link: %s" % link
            metadata = extract_metadata(item)
            metadata['link'] = link

            # save proyecto data into file
            save_project(metadata)
            
            generate_html()
        else:
            print "* we got already that link: %s" % link

    f.close()



    

if __name__ == "__main__":
    main()
