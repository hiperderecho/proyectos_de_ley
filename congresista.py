#!/usr/bin/env python
# -*- coding: utf-8 -*-


import codecs
import os.path
import json
import sys
import string
import re
import config

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
        filename = os.path.join(config.base_folder, filename)
        return filename

def hiperlink_congre(congresistas):
    # tries to make a hiperlink for each congresista name to its own webpage
    for name in congresistas.split("; "):
        filename = convert_name_to_filename(name)
        if filename:
            filename = filename.replace("index.html", "")
            link = "<a href='http://"
            link += filename.replace(config.base_folder, config.base_url)
            link += "' title='ver todos sus proyectos'>"
            link += name + "</a>"
            congresistas = congresistas.replace(name, link)
    return congresistas

def myjson(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ':'))

def prettify(item):
    out = ""
    out += "\n<div>\n"
    out += "<p>"
    out += "<a href='http://" + config.base_url + "proyecto/" + str(item['id'])
    out += "' title='Permalink'>"
    out += "<b>" + item['numero_proyecto'] + "</b></a>"
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

    html_file = item['numero_proyecto'].replace("/", "_") + ".html"
    html_file = os.path.join("pdf", html_file)
    if os.path.isfile(html_file): 
        out += " <a class='btn btn-lg btn-primary'"
        out += " href='" + html_file + "' role='button'>OCR</a>\n"

    out += "</div>\n"
    out += "<hr>\n"
    return out


def generate_congre_html(congre_data):
    name = congre_data['name'].replace(",", "").lower()
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
        path = os.path.join(config.base_folder, path)

        filename = os.path.join(path, "index.html")
        filename = os.path.join(config.base_folder, filename)

        # html files should go into its own folder
        if not os.path.exists(path):
            os.makedirs(path)

        f = codecs.open(os.path.join(config.current_folder, "base.html"), "r", "utf-8")
        base_html = f.read()
        f.close()

        content = ""
        for i in congre_data['data']:
            content += prettify(i) + "----------"
        html = string.replace(base_html, 
                    "{% titulo %}",
                    "<h2>" + congre_data['name'] + "</h2>")
        if config.base_url:
            html = string.replace(html, "{% base_url %}", config.base_url)

        # save as json object instead
        f = codecs.open(os.path.join(path, "html.json"), "w", "utf-8")
        f.write(json.dumps(content.strip().split("----------"), sort_keys=True, indent=4, separators=(',', ':')))
        f.close()

        f = codecs.open(filename, "w", "utf-8")
        f.write(html)
        f.close()

def get_link(names):
    json_file = os.path.join(config.base_folder, "proyectos_data.json")
    if os.path.isfile(json_file):
        f = codecs.open(json_file, "r", "utf-8")
        data = json.loads(f.read())
        f.close()
    else:
        sys.exit("No file %s" % json_file)

    list_congresistas = []
    for i in data:
        congresistas = i['congresistas'].split("; ")
        for congre in congresistas:
            if congre not in list_congresistas:
                list_congresistas.append(congre)

    for congre in list_congresistas:
        congre_data = {'name': congre}
        congre_data['data'] = []
        for item in data:
            to_data = {}
            if congre in item['congresistas']: 
                if 'codigo' in item:
                    to_data['codigo'] = item['codigo']
                if 'titulo' in item:
                    to_data['titulo'] = item['titulo']
                if 'numero_proyecto' in item:
                    to_data['numero_proyecto'] = item['numero_proyecto']
                if 'pdf_url' in item:
                    to_data['pdf_url'] = item['pdf_url']
                if 'link_to_pdf' in item:
                    to_data['link_to_pdf'] = item['link_to_pdf']
                if 'fecha_presentacion' in item:
                    to_data['fecha_presentacion'] = item['fecha_presentacion']
                if 'congresistas' in item:
                    to_data['congresistas'] = item['congresistas']
                congre_data['data'].append(to_data) 
        # now make a HTML for this congresista
        generate_congre_html(congre_data)


if __name__ == "__main__":
    # this is for debugging
    names = """Rondon Fudinaga, Gustavo Bernardo; Acu\u00f1a Peralta, Virgilio;
                Belaunde Moreyra, Martin; Capu\u00f1ay Quispe, Esther Yovana;
                Wong Pujada, Enrique; Zeballos Salinas, Vicente Antonio"""
    get_link(names)

