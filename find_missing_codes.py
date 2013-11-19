# -*- coding: utf-8 -*-

import codecs
import json
import sys

if len(sys.argv) < 2:
    print "This script Finds which codes are missing in our records"
    print "command.py jsonFile"
    sys.exit()

f = codecs.open(sys.argv[1].strip(), "r", "utf-8")
input_json = json.loads(f.read())
f.close()

i_next = ""
for i in input_json:
    i = int(i['codigo'])
    if i_next != "":
        if i_next != i:
            print "We dont have record %i" % i_next
    i_next = i - 1


