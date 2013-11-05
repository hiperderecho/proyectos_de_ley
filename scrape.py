#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


tor = True
debug = False

if tor:
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket



def parse_names(string):
    """ 
    Parse string of names. Output only family name as list.
    """
    names = []
    for i in string.split(","):
        i = re.sub("\s{2}.+", "", i)
        names.append(i)
    return names

def prettify(metadata):
    out = "\n<ul>\n"
    for k, v in metadata.items():
        out += "<li><b>" + k + ":</b> " + v + "</li>\n";
    out += "</ul>"
    return out
        

def extract_pdf_url(link):
    #link = "http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/02787?opendocument"
    pdf_soup = get(link)
    for i in pdf_soup.find_all("a"):
        if i['href'].endswith('pdf'):
            return i['href']


def extract_metadata(link):
    if debug:
        f = open("fibri.html", "r")
        html_doc = f.read()
        f.close()
        project_soup = BeautifulSoup(html_doc)
    else:
        project_soup = get(link)

    metadata = {}
    for item in project_soup.find_all("input"):
        if item['name'] == "CodIni_web_1":
            metadata['numero_proyecto'] = item['value']
        if item['name'] == "DesGrupParla":
            metadata['grupo_parlamentario'] = item['value']
        if item['name'] == "TitIni":
            metadata['titulo'] = item['value']
        if item['name'] == "NombreDeLaComision":
            metadata['comision'] = item['value']
        if item['name'] == "NomCongre":
            metadata['congresistas'] = item['value']
        if item['name'] == "CodIni":
            metadata['codigo'] = item['value']
        if item['name'] == "fechapre":
            metadata['fecha_presentacion'] = item['value']
    link_to_pdf = 'http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/'
    link_to_pdf += metadata['codigo'] + '?opendocument'
    metadata['link_to_pdf'] = link_to_pdf
    metadata['pdf_url'] = extract_pdf_url(link_to_pdf)
    return metadata

def extract_doc_links(soup):
    our_links = []
    for link in soup.find_all("a"):
        if re.search("201[0-9]-CR$", link.get_text()):
            href = link.get("href")
            if href.endswith("ocument"):
                our_link = "http://www2.congreso.gob.pe" + "/" + href
                our_link = re.sub("//Sicr","/Sirc", our_link)
                our_links.append(our_link)
    return our_links

def get(url):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Accept-Charset', 'utf-8')]
    request = urllib2.Request(url)
    request.add_header('Cache-Control','max-age=0')
    response = opener.open(request)
    soup = BeautifulSoup(response.read().decode("utf-8"))
    return soup

## ------------------------------------------------
def main():
    url = "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/PAporNumeroInverso?OpenView"
    soup = get(url)
    links = extract_doc_links(soup)

    f = codecs.open("proyectos_de_ley.html", "w", "utf-8")
    f.write("<html><head><title>Proyectos de ley</title>")
    f.write("\n<meta charset='utf-8'>\n</head><body>")
    f.write("\n<h1>Proyectos de ley</h1>\n")
    for link in links:
        metadata = extract_metadata(link)
        metadata = prettify(metadata)
        f.write(metadata)

    f.write("</body></html>")
    f.close()



    

if __name__ == "__main__":
    main()
