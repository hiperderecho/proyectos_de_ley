#!/usr/bin/env python
# -*- coding: utf-8 -*-


import codecs
import os.path
import json
import sys
import string
import re

def prettify(item):
    print item
    sys.exit()
    out = ""
    out += "\n<div>\n"
    out += "<p><b>" + item['numero_proyecto'] + "</b>\n"
    out += "<h4>" + item['titulo'] +  "</h4>\n"
    out += "<p>" + item['congresistas'] + "</p>\n"

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
    i = 0
    path = ""
    while( i < 3 ):
        path += name[i]
        if i < 2:
            path += "_"
        i = i + 1
    path = os.path.join("congresista", path)
    filename = os.path.join(path, "index.html")
    print path
    print filename

    # html files should go into its own folder
    if not os.path.exists(path):
        os.makedirs(path)

    f = codecs.open("base.html", "r", "utf-8")
    base_html = f.read()
    f.close()

    html = string.replace(base_html, 
                    "{% titulo %}",
                    "<h1>" + congre_data['name'] + "</h1>")
    content = ""
    if "data" in congre_data:
        print prettify(congre_data['data'])
    #html = string.replace(base_html, "{% content %}", prettify(data))

    f = codecs.open(filename, "w", "utf-8")
    f.write(html)
    f.close()

def get_link(names):
    json_file = "proyectos_data.json"
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
            if congre in item['congresistas']: 
                if 'titulo' in item:
                    congre_data['data'].append({"titulo": item['titulo']})
                if 'numero_proyecto' in item:
                    congre_data['data'].append({"numero_proyecto":
                            item['numero_proyecto']})
                if 'pdf_url' in item:
                    congre_data['data'].append({"pdf_url": item['pdf_url']})
                if 'link_to_pdf' in item:
                    congre_data['data'].append({"link_to_pdf":
                            item['link_to_pdf']})
                if 'fecha_presentacion' in item:
                    congre_data['data'].append({"fecha_presentacion":
                            item['fecha_presentacion']})
        # now make a HTML for this congresista
        generate_congre_html(congre_data)
    sys.exit()


if __name__ == "__main__":
    # this is for debugging
    names = """Rondon Fudinaga, Gustavo Bernardo; Acu\u00f1a Peralta, Virgilio;
                Belaunde Moreyra, Martin; Capu\u00f1ay Quispe, Esther Yovana;
                Wong Pujada, Enrique; Zeballos Salinas, Vicente Antonio"""
    get_link(names)

