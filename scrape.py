#!/usr/bin/python
# -*- coding: utf-8 -*-

import dataset
import sqlalchemy
import json
#import socks
import cookielib
import shutil
import socket
from bs4 import BeautifulSoup
import requests
import sys
import re
from os import listdir
import codecs
import glob
import urllib2
import time
import random
import string
import os.path
import urlparse
import congresista # script to create pages for each one
import config # our folder paths
import sqlite3 as lite


random.seed();  
tor = False
debug = True

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
    f = codecs.open(os.path.join(config.current_folder, "base.html"), "r", "utf-8")
    base_html = f.read()
    f.close()

    f = codecs.open(os.path.join(config.base_folder, "proyectos_data.json"), "r", "utf-8")
    data = json.loads(f.read())
    f.close()

    # save as json object instead
    f = codecs.open(os.path.join(config.base_folder, "html.json"), "w", "utf-8")
    f.write(json.dumps(prettify(data).strip().split("----------"), sort_keys=True, indent=4, separators=(',', ':')))
    f.close()


    if config.base_url:
        html = string.replace(base_html, "{% base_url %}", "/" + config.base_url)
        html = string.replace(html, "{% titulo %}", "<h1 id='proyectos_de_ley'>Proyectos de Ley</h1>")

    f = codecs.open(os.path.join(config.base_folder, "index.html"), "w", "utf-8")
    f.write(html)
    f.close()

def update_search_engine():
    f = codecs.open(os.path.join(config.current_folder, "search.js"), "r", "utf-8")
    base_html = f.read()
    f.close()

    if config.base_url:
        html = string.replace(base_html, "{% base_url %}", "/" + config.base_url)

    f = codecs.open(os.path.join(config.base_folder, "search.js"), "w", "utf-8")
    f.write(html)
    f.close()

def hiperlink_congre(congresistas):
    # tries to make a hiperlink for each congresista name to its own webpage
    for name in congresistas.split("; "):
        filename = convert_name_to_filename(name)
        if filename:
            filename = os.path.join(config.base_folder, filename)
            if os.path.isfile(filename):
                filename = filename.replace("index.html", "")
                filename = "http://" + filename.replace(config.base_folder, config.base_url)
                link = "<a href='"
                link += filename
                link += "' title='ver todos sus proyectos'>"
                link += name + "</a>"
                congresistas = congresistas.replace(name, link)
    return congresistas

def convert_name_to_filename(name):
    # takes a congresista name and returns its html filename
    name = name.replace(",", "").lower()
    name = name.encode("ascii", "ignore")
    name = name.split(" ")
    
    if len(name) > 2:
        i = 0
        path = ""
        while( i < 3 ):
            path += name[i]
            if i < 2:
                path += "_"
            i = i + 1
        path = os.path.join("congresista", path)
        filename = os.path.join(path, "index.html")
        return filename


def prettify(data):
    out = ""
    for item in data:
        out += "<div>\n"
        out += "<p><b>" + item['numero_proyecto'] + "</b>\n"
        out += "<h4>" + item['titulo'] +  "</h4>\n"
        out += "<p>" + hiperlink_congre(item['congresistas']) + "</p>\n"

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
        out += "----------"
    return out
        

def extract_pdf_url(link):
    # also downloads to local folder
    codigo = re.search("([0-9]{5})\?", link).groups()[0]
    filename = os.path.join(config.current_folder, "pages")
    filename = os.path.join(filename, codigo + ".html")
    if not os.path.isfile(filename):
        try:
            pdf_soup = get(link)
        except:
            # Algunos proyectos de ley no tienen link hacia PDFs
            return "none"
    else:
        f = codecs.open(filename, "r", "utf-8")
        html = f.read()
        f.close()
        pdf_soup = BeautifulSoup(html)
    try:
        for i in pdf_soup.find_all("a"):
            if re.search("pdf$", i['href'], re.I):
                my_pdf_link = str(i['href'])
                return my_pdf_link
    except:
        # Algunos proyectos de ley no tienen link hacia PDFs
        return "none"

def extract_pdf_url_from_local_file(filename):
    f = codecs.open(filename, "r", "utf-8")
    html = f.read()
    f.close()
    pdf_soup = BeautifulSoup(html)
    try:
        for i in pdf_soup.find_all("a"):
            if re.search("pdf$", i['href'], re.I):
                my_pdf_link = str(i['href'])
                return my_pdf_link
    except:
        # Algunos proyectos de ley no tienen link hacia PDFs
        return "none"



def extract_metadata(filename):
    f = codecs.open(filename, "r", "utf-8")
    html = f.read()
    f.close()

    project_soup = BeautifulSoup(html)

    this_metadata = dict()
    for item in project_soup.find_all("input"):
        if item['name'] == "SumIni":
            this_metadata['titulo'] = item['value']
        if item['name'] == "CodIni_web_1":
            this_metadata['numero_proyecto'] = item['value']
            print "* numero_proyecto: %s" % this_metadata['numero_proyecto']
        #if item['name'] == "DesGrupParla":
            #metadata['grupo_parlamentario'] = item['value']
        #if item['name'] == "NombreDeLaComision":
            #metadata['comision'] = item['value']
        if item['name'] == "NomCongre":
            this_metadata['congresistas'] = parse_names(item['value'])
        if item['name'] == "CodIni":
            this_metadata['codigo'] = item['value']
        if item['name'] == "fechapre":
            this_metadata['fecha_presentacion'] = item['value']
            print "* fecha_presentacion: %s" % this_metadata['fecha_presentacion']
    link_to_pdf = 'http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/' + this_metadata['codigo'] + '?opendocument'
    try:
        this_metadata['link_to_pdf'] = link_to_pdf
        print this_metadata['link_to_pdf']

        this_metadata['pdf_url'] = extract_pdf_url(link_to_pdf)
    except:
        print "no link to pdf"

    # don't do this for now as OCR is not so critical
    #get_pdf(metadata['pdf_url'], metadata['numero_proyecto'])

    # Algunos proyectos de Ley no tienen links hacia PDFs
    if this_metadata['pdf_url'] == "none":
        del this_metadata['pdf_url']
        del this_metadata['link_to_pdf']
    return this_metadata

def extract_expediente_link(page):
    f = open(page, "r")
    html_doc = f.read()
    f.close()
    soup = BeautifulSoup(html_doc)

    for item in soup.find_all("input"):
        if item['name'] == "CodIni":
            codigo = item['value']
            expediente_link = 'http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/' + codigo + '?opendocument'
            return [expediente_link, codigo]


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

def create_database():
    database_file = os.path.join(config.base_folder, "leyes.db")
    if not os.path.isfile(database_file):
        try:
            db = dataset.connect('sqlite:///leyes.db')
            table = db.create_table("proyectos")
            table.create_column('codigo', sqlalchemy.String)
            table.create_column('numero_proyecto', sqlalchemy.String)
            table.create_column('congresistas', sqlalchemy.Text)
            table.create_column('fecha_presentacion', sqlalchemy.String)
            table.create_column('link_to_pdf', sqlalchemy.Text)
            table.create_column('pdf_url', sqlalchemy.Text)
            table.create_column('titulo', sqlalchemy.Text)
        except:
            pass

def insert_data():
    folder = os.path.join(config.current_folder, "pages")
    files = glob.glob(os.path.join(folder, "*html"))

    db = dataset.connect('sqlite:///leyes.db')
    table = db['proyectos']

    for file in files:
        res = re.search("^(.+)\.html", os.path.basename(file))
        if res and len(res.groups()[0]) == 32:
            met = extract_metadata(file)
            print congresista.myjson(met)
            data_to_insert = []
            if not table.find_one(codigo=met['codigo']):
                data_to_insert.append(dict(
                            codigo = met['codigo'],
                            numero_proyecto = met['numero_proyecto'],
                            congresistas = met['congresistas'],
                            fecha_presentacion = met['fecha_presentacion'],
                            link_to_pdf = met['link_to_pdf'],
                            pdf_url = met['pdf_url'],
                            titulo = met['titulo']
                            ))

            table.insert_many(data_to_insert)    



def processed_links():
    f = False
    processed_links = []
    # Returns a list of links found in our data file "proyectos_data.json"
    if os.path.isfile(os.path.join(config.base_folder, "proyectos_data.json")):
        f = codecs.open(os.path.join(config.base_folder, "proyectos_data.json"), "r", "utf-8")
        try: 
            data = json.loads(f.read());
            if debug:
                print "Found %i items in file proyectos_data.json" % len(data)
        except:
            if f:
                f.close()
            return processed_links
    else:
        return processed_links


    if f:
        f.close()

    for item in data:
        if "link_to_pdf" in item:
            processed_links.append(item['link'])

    return processed_links


# downloads PDF and saves to current folder
def get_pdf(url, numero_proyecto):
    if not os.path.isdir("pdf"):
        os.mkdir("pdf")

    r = requests.get(url)
    numero_proyecto = re.sub("/", "_", numero_proyecto)
    try:
        with open(os.path.join("pdf", numero_proyecto + ".pdf"), "wb") as fd:
            for chunk in r.iter_content(100):
                fd.write(chunk)
    except:
        print "** Couldn't get PDF file"
    

def get(url):
    #n = random.random()*5;  
    #time.sleep(n);  
    #print "* sleep for %f" % n
    if debug:
        print "This url %s" % url
        if not os.path.isdir(os.path.join(config.current_folder, "pages")):
            os.mkdir(os.path.join(config.current_folder, "pages"))
        if re.search("(OpenView)(&Start=)?([0-9]*)", url):
            s = re.search("(OpenView)(&Start=)?([0-9]*)", url)
            filename = os.path.join(config.current_folder, "pages") + "/" + s.groups()[0] + s.groups()[2] + ".html"
        elif re.search("(\w+)\?opendocument", url):
            s = re.search("(\w+)\?opendocument", url)
            filename = os.path.join(config.current_folder, "pages") + "/" + s.groups()[0] + ".html"

        print "This filename %s" % filename
        if not os.path.isfile(filename) or os.stat(filename).st_size < 2:
            f = codecs.open(filename, "w", "utf-8")
            request = urllib2.Request(url)
            request.add_header('Cache-Control','max-age=0')
            response = opener.open(request)
            this_page = response.read().decode("utf-8")
            f.write(this_page)
            f.close()
            soup = BeautifulSoup(this_page)
            return soup
        else:
            print "Getting info from local file %s" % filename
            f = codecs.open(filename, "r", "utf-8")
            this_page = f.read()
            f.close()
            soup = BeautifulSoup(this_page)
            return soup
            

    request = urllib2.Request(url)
    request.add_header('Cache-Control','max-age=0')
    response = opener.open(request)
    this_page = response.read().decode("utf-8")

    soup = BeautifulSoup(this_page)
    return soup

def download_exp_pagina(link):
    # link = [url, codigo]

    filename = os.path.join(config.current_folder, "pages")
    filename = os.path.join(filename, link[1] + ".html")
    if not os.path.isfile(filename) or os.stat(filename).st_size < 2:
        print "Downloading %s" % link[0]
        request = urllib2.Request(link[0])
        request.add_header('Cache-Control','max-age=0')
        response = opener.open(request)
        this_page = response.read().decode("utf-8")

        f = codecs.open(filename, "w", "utf-8")
        f.write(this_page)
        f.close()
    else:
        return "downloaded already"

# save proyecto data into file
def save_project(metadata):
    json_file = os.path.join(config.base_folder, "proyectos_data.json")
    if os.path.isfile(json_file):
        f = codecs.open(json_file, "r", "utf-8")
        data = f.read()
        f.close()
        if len(data) < 2:
            file_empty = True
        else:
            file_empty = False

    else:
        file_empty = True

    if file_empty:
        data = []
        data.append(metadata)
        f = codecs.open(json_file, "w", "utf-8")
        f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
        f.close()
    else:
        f = codecs.open(json_file, "r", "utf-8")
        data = json.loads(f.read())
        f.close()

        # check if need to update item
        saved = False
        new_data = []
        for i in data:
            if i['codigo'] == metadata['codigo']:
                # update our item
                print "# update our item"
                i = metadata
                saved = True
                new_data.append(i)

        if len(new_data) > 0: 
            f = codecs.open(os.path.join(config.base_folder, "proyectos_data.json"), "w", "utf-8")
            f.write(json.dumps(new_data, sort_keys=True, indent=4, separators=(',', ':')))
            f.close()
            saved = True

        if not saved:
            # append our item then
            data.append(metadata)
            f = codecs.open(os.path.join(config.base_folder, "proyectos_data.json"), "w", "utf-8")
            f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
            f.close()



## ------------------------------------------------
def main():
    """
    url_inicio = 'http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/PAporNumeroInverso?OpenView'
    urls = [url_inicio]

    # from 100 to 2900 to get from 0001/2011-CR
    for i in range(2800, 3000, 100):
        urls.append(url_inicio + "&Start=" + str(i))


    for url in urls:
        print "Doing URL %s" % url
        soup = get(url)
        links = extract_doc_links(soup)
        if debug:
            print "Found %i links" % len(links)

        for item in links:
            link = item['link']
            get(link)

    # Create needed folders
    page_folder = os.path.join(config.current_folder, "pages")
    if not os.path.isdir(page_folder):
        os.mkdir(page_folder)


    # We need to download the expediente page for each link page
    folder = os.path.join(config.current_folder, "pages")
    pages = glob.glob(os.path.join(folder, "*html"))
    for page in pages:
        link = extract_expediente_link(page)
        if link:
            local_exp_pagina = os.path.join(config.current_folder, "pages")
            local_exp_pagina = os.path.join(local_exp_pagina, link[1] + ".html")
    
            # Try to download if we dont have it locally
            download_exp_pagina(link)

    # We need to add info to our SQLite database
    """
    create_database()
    insert_data()
"""
        if re.search("^[0-9]{5}\.html", page):
            print page
            sys.exit()

            if link not in processed_links():
                print "* getting link: %s" % link
                metadata = extract_metadata(item)
                metadata['link'] = link

                # save proyecto data into file
                save_project(metadata)
                
                generate_html()
                update_search_engine()
                print "updated search engine"
                congresista.get_link(metadata['congresistas'])

                # copy files
                if not os.path.isfile(os.path.join(config.base_folder, "paginator.js")):
                    shutil.copy2(os.path.join(config.current_folder, "paginator.js"),
                                os.path.join(config.base_folder, "paginator.js"))
                if not os.path.isfile(os.path.join(config.base_folder, "jquery.bootpag.js")):
                    shutil.copy2(os.path.join(config.current_folder, "jquery.bootpag.js"),
                                os.path.join(config.base_folder, "jquery.bootpag.js"))
                congre_dummy_index = os.path.join(config.base_folder, "congresista")
                congre_dummy_index = os.path.join(congre_dummy_index, "index.html")
                if not os.path.isfile(congre_dummy_index):
                    f = codecs.open(congre_dummy_index, "w", "utf-8")
                    f.write("<html><head></head><body></body></html>")
                    f.close()


            else:
                pass
                #print "* we got already that link: %s" % link
"""



if __name__ == "__main__":
    main()
