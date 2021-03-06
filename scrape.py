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
import short_url
import glob
import urllib2
import time
import datetime
import random
import string
import os.path
import urlparse
import congresista # script to create pages for each one
import config # our folder paths
import create_rss # our RSS builder
import create_sitemap # our SITEMAP builder
import sqlite3 as lite
from unidecode import unidecode


random.seed();  
tor = False
debug = True

if tor:
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('Accept-Charset', 'utf-8')]



def generate_congresista_json():
    print "Generating html.json files for congresista"
    db = dataset.connect("sqlite:///leyes.db")
    res = db.query("SELECT DISTINCT congresistas FROM proyectos")
    congresistas = []
    for i in res:
        nombres = i['congresistas'].split(";")
        congresistas += nombres
    #clean names
    new_congresistas = []
    for i in congresistas:
        i = i.strip()
        if i not in new_congresistas and i != "Sin Grupo" and i != "":
            new_congresistas.append(i)

    for i in new_congresistas:
        query = "SELECT * FROM proyectos WHERE congresistas like '%" + i + "%' "
        query += "ORDER BY codigo DESC"
        res = db.query(query)

        congre_data = {'name': i}
        congre_data['data'] = []
        for item in res:
            to_data = {}
            if i in item['congresistas']: 
                if 'short_url' in item:
                    to_data['short_url'] = item['short_url']
                if 'codigo' in item:
                    to_data['codigo'] = item['codigo']
                if 'titulo' in item:
                    to_data['titulo'] = item['titulo']
                if 'numero_proyecto' in item:
                    to_data['numero_proyecto'] = item['numero_proyecto']
                if 'seguimiento_page' in item:
                    to_data['seguimiento_page'] = item['seguimiento_page']
                if 'pdf_url' in item:
                    to_data['pdf_url'] = item['pdf_url']
                if 'link_to_pdf' in item:
                    to_data['link_to_pdf'] = item['link_to_pdf']
                if 'fecha_presentacion' in item:
                    to_data['fecha_presentacion'] = item['fecha_presentacion']
                if 'congresistas' in item:
                    to_data['congresistas'] = item['congresistas']
                congre_data['data'].append(to_data) 
        congresista.generate_congre_html(congre_data)




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
        html = string.replace(base_html, "{% base_url %}", config.base_url)
        html = string.replace(html, "{% titulo %}", "<h1 id='proyectos_de_ley'>Proyectos de Ley</h1>")

    f = codecs.open(os.path.join(config.base_folder, "index.html"), "w", "utf-8")
    f.write(html)
    f.close()

def update_search_engine():
    f = codecs.open(os.path.join(config.current_folder, "search.js"), "r", "utf-8")
    base_html = f.read()
    f.close()

    if config.base_url:
        html = string.replace(base_html, "{% base_url %}", config.base_url)

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
    name = unidecode(name)
    #name = name.encode("ascii", "ignore")
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


def prettify(item):
    out = ""
    out += "\n<div>\n"
    out += "<p>"
    out += "<a href='http://" + config.base_url + "p/" + str(item['short_url'])
    out += "' title='Permalink'>"
    out += "<b>" + item['numero_proyecto'] + "</b></a>"
    out += "<h4>" + item['titulo'] +  "</h4>\n"
    out += "<p>" + hiperlink_congre(item['congresistas']) + "</p>\n"

    if 'pdf_url' in item:
        out += "<a class='btn btn-lg btn-primary'"
        try:
            out += " href='" + item['pdf_url'] + "' role='button'>PDF</a>"
        except:
            out += " disabled='disabled' href='#' role='button'>PDF</a>"
    else:
        out += "<a class='btn btn-lg btn-primary disabled'"
        out += " href='#' role='button'>Sin PDF</a>"

    if 'link_to_pdf' in item:
        out += " <a class='btn btn-lg btn-primary'"
        out += " href='" + item['link_to_pdf'] + "' role='button'>EXPEDIENTE</a>"
    else:
        out += " <a class='btn btn-lg btn-primary disabled'"
        out += " href='#' role='button'>Sin EXPEDIENTE</a>"

    if 'seguimiento_page' in item:
        if item['seguimiento_page'] != "":
            out += " <a class='btn btn-lg btn-primary'"
            out += " href='" + item['seguimiento_page'] + "' role='button'>Seguimiento</a>"


    out += "</div>\n"
    out += "<hr>\n"
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
        pattern = re.compile("/PL" + str(codigo) + "[0-9]+\.pdf$")
        for i in pdf_soup.find_all("a"):
            if re.search(pattern, i['href']):
                my_pdf_link = str(i['href'])
                return my_pdf_link
    except:
        # Algunos proyectos de ley no tienen link hacia PDFs
        return "none"

def extract_pdf_url_from_local_file(filename):
    codigo = re.search("([0-9]{5})\.html", filename).groups()[0]
    f = codecs.open(filename, "r", "utf-8")
    html = f.read()
    f.close()
    pdf_soup = BeautifulSoup(html)
    try:
        pattern = re.compile("/PL" + str(codigo) + "[0-9]+\.+pdf$")
        for i in pdf_soup.find_all("a"):
            if re.search(pattern, i['href']):
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
            #print "* numero_proyecto: %s" % this_metadata['numero_proyecto']
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
            #print "* fecha_presentacion: %s" % this_metadata['fecha_presentacion']
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
    print "Creating database"
    database_file = os.path.join(config.base_folder, "leyes.db")
    if not os.path.isfile(database_file):
        try:
            db = dataset.connect('sqlite:///leyes.db')
            table = db.create_table("proyectos")
            table.create_column('codigo', sqlalchemy.String)
            table.create_column('short_url', sqlalchemy.String)
            table.create_column('numero_proyecto', sqlalchemy.String)
            table.create_column('congresistas', sqlalchemy.Text)
            table.create_column('fecha_presentacion', sqlalchemy.String)
            table.create_column('link_to_pdf', sqlalchemy.Text)
            table.create_column('pdf_url', sqlalchemy.Text)
            table.create_column('timestamp', sqlalchemy.String)
            table.create_column('titulo', sqlalchemy.Text)
        except:
            pass

def insert_data():
    print "Inserting data to database"
    folder = os.path.join(config.current_folder, "pages")
    files = [f for f in os.listdir(folder) if re.search("\w{32}\.html", f)]

    db = dataset.connect('sqlite:///leyes.db')
    table = db['proyectos']

    for file in files:
        seguimiento_page = file
        seguimiento_page = file.replace(".html", "")
        seguimiento_page = "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/Sicr/TraDocEstProc/CLProLey2011.nsf/PAporNumeroInverso/" + seguimiento_page + "?opendocument" 
        file = os.path.join("pages", file)
        file = os.path.join(config.current_folder, file)

        # get date modification of file
        last_modified = os.stat(file).st_mtime
        # was modified less than two days ago?
        d = time.time() - last_modified
        #print "last modified %i days ago" % datetime.timedelta(seconds=d).days

        if datetime.timedelta(seconds=d).days < 3:
            met = extract_metadata(file)
            # construct this project's short-url
            string = config.legislatura + met['codigo']
            url = short_url.encode_url(int(string))
            met['short_url'] = url
            if met['fecha_presentacion']:
                s = met['fecha_presentacion']
                met['timestamp'] = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
            else:
                met['timestamp'] = time.mktime(datetime.datetime.now().timetuple())

            data_to_insert = []
            if not table.find_one(short_url=met['short_url']):
                data_to_insert.append(dict(
                        codigo = met['codigo'],
                        short_url = met['short_url'],
                        numero_proyecto = met['numero_proyecto'],
                        congresistas = met['congresistas'],
                        fecha_presentacion = met['fecha_presentacion'],
                        link_to_pdf = met['link_to_pdf'],
                        pdf_url = met['pdf_url'],
                        seguimiento_page = seguimiento_page,
                        timestamp = met['timestamp'],
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
    url_inicio = 'http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/PAporNumeroInverso?OpenView'
    urls = [url_inicio]

    # from 100 to 2900 to get from 0001/2011-CR
    for i in range(100, 500, 100):
        urls.append(url_inicio + "&Start=" + str(i))

    # remove most recent pages from local disk
    if os.path.isfile("pages/OpenView.html"):
        os.remove("pages/OpenView.html")
    if os.path.isfile("pages/OpenView100.html"):
        os.remove("pages/OpenView100.html")

    for url in urls:
        print "Doing URL %s" % url
        soup = get(url)
        links = extract_doc_links(soup)
        if debug:
            print "Found %i links" % len(links)

        for item in links:
            link = item['link']
            get(link)
            print ""

    # Create needed folders
    page_folder = os.path.join(config.current_folder, "pages")
    print "Working on folder ``pages``"
    if not os.path.isdir(page_folder):
        os.mkdir(page_folder)


    # We need to download the expediente page for each link page
    folder = os.path.join(config.current_folder, "pages")
    pages = [f for f in os.listdir(folder) if re.search("\w{32}\.html", f)]

    for page in pages:
        file = os.path.join("pages", page)

        # get date modification of file
        last_modified = os.stat(file).st_mtime
        # was modified less than two days ago?
        d = time.time() - last_modified
        #print "last modified %i days ago" % datetime.timedelta(seconds=d).days

        if datetime.timedelta(seconds=d).days < 3:
            page = os.path.join(folder, page)
            link = extract_expediente_link(page)
            if link:
                local_exp_pagina = os.path.join(config.current_folder, "pages")
                local_exp_pagina = os.path.join(local_exp_pagina, link[1] + ".html")
    
                # Try to download if we dont have it locally
                print "Need page %s" % link[1]
                print download_exp_pagina(link)

    # We need to add info to our SQLite database
    create_database()
    insert_data()
    generate_congresista_json()

    create_rss.create_rss()
    create_sitemap.create_sitemap()

    # copy files
    print "Copying files to base_folder..."
    f = codecs.open("paginator.js", "r", "utf-8")
    base_html = f.read()
    f.close()
    html = string.replace(base_html, "{% base_url %}", config.base_url)
    f = codecs.open(os.path.join(config.base_folder, "paginator.js"), "w", "utf-8")
    f.write(html)
    f.close()

    print "Copying index.html"
    f = codecs.open("base.html", "r", "utf-8")
    base_html = f.read()
    f.close()
    # get latest 20 proyects
    db = dataset.connect("sqlite:///leyes.db")
    res = db.query("SELECT * FROM proyectos ORDER BY codigo DESC LIMIT 20")
    out = ""
    for i in res:
        out += prettify(i)

    html = string.replace(base_html, "{% base_url %}", config.base_url)
    html = string.replace(html, "{% titulo %}", "<h1 id='proyectos_de_ley'>Proyectos de Ley</h1>")
    html = string.replace(html, '"contenido" class="container">', '"contenido" class="container">' + out)
    f = codecs.open(os.path.join(config.base_folder, "index.html"), "w", "utf-8")
    f.write(html)
    f.close()

    f = codecs.open("search.js", "r", "utf-8")
    base_html = f.read()
    f.close()
    html = string.replace(base_html, "{% base_url %}", config.base_url)
    f = codecs.open(os.path.join(config.base_folder, "search.js"), "w", "utf-8")
    f.write(html)
    f.close()

    shutil.copy2(os.path.join(config.current_folder, "create_sitemap.py"),
                    os.path.join(config.base_folder, "create_sitemap.py"))
    shutil.copy2(os.path.join(config.current_folder, "sitemap.xml"),
                    os.path.join(config.base_folder, "sitemap.xml"))
    shutil.copy2(os.path.join(config.current_folder, "rss.xml"),
                    os.path.join(config.base_folder, "rss.xml"))
    shutil.copy2(os.path.join(config.current_folder, "hd.png"),
                    os.path.join(config.base_folder, "hd.png"))
    shutil.copy2(os.path.join(config.current_folder, "g_rss.png"),
                    os.path.join(config.base_folder, "g_rss.png"))
    shutil.copy2(os.path.join(config.current_folder, "g_twitter.png"),
                    os.path.join(config.base_folder, "g_twitter.png"))
    shutil.copy2(os.path.join(config.current_folder, "g_facebook.png"),
                    os.path.join(config.base_folder, "g_facebook.png"))
    shutil.copy2(os.path.join(config.current_folder, "create_rss.py"),
                    os.path.join(config.base_folder, "create_rss.py"))
    shutil.copy2(os.path.join(config.current_folder, "config.py"),
                    os.path.join(config.base_folder, "config.py"))
    shutil.copy2(os.path.join(config.current_folder, "base.html"),
                    os.path.join(config.base_folder, "base.html"))
    shutil.copy2(os.path.join(config.current_folder, "jquery.bootpag.js"),
                    os.path.join(config.base_folder, "jquery.bootpag.js"))
    shutil.copy2(os.path.join(config.current_folder, "current_tab.js"),
                    os.path.join(config.base_folder, "current_tab.js"))
    shutil.copy2(os.path.join(config.current_folder, "highlighter.js"),
                    os.path.join(config.base_folder, "highlighter.js"))
    shutil.copy2(os.path.join(config.current_folder, ".htaccess"),
                    os.path.join(config.base_folder, ".htaccess"))
    shutil.copy2(os.path.join(config.current_folder, "data_handler.py"),
                    os.path.join(config.base_folder, "data_handler.py"))
    shutil.copy2(os.path.join(config.current_folder, "scrape.py"),
                    os.path.join(config.base_folder, "scrape.py"))
    shutil.copy2(os.path.join(config.current_folder, "congresista.py"),
                    os.path.join(config.base_folder, "congresista.py"))
    shutil.copy2(os.path.join(config.current_folder, "config.py"),
                    os.path.join(config.base_folder, "config.py"))
    shutil.copy2(os.path.join(config.current_folder, "leyes.db"),
                    os.path.join(config.base_folder, "leyes.db"))
    congre_dummy_index = os.path.join(config.base_folder, "congresista")
    congre_dummy_index = os.path.join(congre_dummy_index, "index.html")

    f = codecs.open(congre_dummy_index, "w", "utf-8")
    f.write("<html><head></head><body></body></html>")
    f.close()

    # about page
    about = os.path.join(config.base_folder, "about")
    if not os.path.isdir(about):
        os.mkdir(about)
    about_page = os.path.join(about, "index.html")
    f = codecs.open(os.path.join(config.current_folder, "base.html"), "r", "utf-8")
    base_html = f.read()
    f.close()
    f = codecs.open(about_page, "w", "utf-8")
    html = string.replace(base_html, "<script src=\"http://{% base_url %}paginator.js\"></script>", "")
    html = string.replace(html, "{% base_url %}", config.base_url)
    html = string.replace(html, "{% titulo %}", u"<h1 id='about'>Sobre esta página</h1>")
    out_html = u'''"contenido" class="container">
        <p><strong>proyectosdeley.pe</strong> es un intento de transparentar el
        Congreso y poner al alcance de la mayor cantidad de personas los
        proyectos de ley presentados y discutidos en el parlamento. La
        información mostrada es tomada directamente de la página web del
        Congreso.</p>

        <p>Esta página ha sido desarrollada en forma independiente por la <a
        href="http://www.hiperderecho.org">ONG Hiperderecho</a>, una organización civil
        peruana sin fines de lucro dedicada a investigar, facilitar el entendimiento
        público y promover el respeto de los derechos y libertades en entornos
        digitales.</p>'''
    html = string.replace(html, '"contenido" class="container">', out_html)
    
    f.write(html)
    f.close()

    print "Copied all files to base_folder..."
    print "ready"



if __name__ == "__main__":
    main()
