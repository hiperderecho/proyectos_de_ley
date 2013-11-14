import codecs
import os
import json
import config
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
        out += "\n<div>\n"
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
    return out

f = codecs.open(os.path.join(config.base_folder, "proyectos_data.json"), "r", "utf-8")
data = json.loads(f.read())
f.close()

print json.dumps(prettify(data).strip().split("<hr>\n"))
