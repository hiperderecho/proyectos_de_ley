import config
import short_url
import time
import datetime
import sys
import os
import re
import dataset
import scrape


folder = os.path.join(config.current_folder, "pages")
files = [f for f in os.listdir(folder) if re.search("\w{32}\.html", f)]
#for i in files:
    #print i
#sys.exit()

db = dataset.connect('sqlite:///leyes.db')
table = db['proyectos']

for file in files:
    seguimiento_page = file
    seguimiento_page = file.replace(".html", "")
    seguimiento_page = "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/Sicr/TraDocEstProc/CLProLey2011.nsf/PAporNumeroInverso/" + seguimiento_page + "?opendocument" 
    file = os.path.join("pages", file)
    file = os.path.join(config.current_folder, file)

    try:
        met = scrape.extract_metadata(file)
    except:
        print "Couldn't extract metadata of file %s" % file
    # construct this project's short-url
    string = config.legislatura + met['codigo']
    url = short_url.encode_url(int(string))
    met['short_url'] = url

    data_to_insert = dict(short_url=met['short_url'], 
                      seguimiento_page=seguimiento_page)

    print "Uploading ",  met['short_url'], seguimiento_page
    res = table.find_one(short_url=met['short_url'], seguimiento_page="")
    table.update(data_to_insert, ['short_url'])    

