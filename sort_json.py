# -*- coding: utf-8 -*-

import codecs
import json
import sys

if len(sys.argv) < 2:
    print "This script sorts a json file"
    print "command.py input output"
    sys.exit()

f = codecs.open(sys.argv[1].strip(), "r", "utf-8")
input_json = json.loads(f.read())
f.close()

sorted_json = sorted(input_json, reverse=True)

f = codecs.open(sys.argv[2].strip(), "w", "utf-8")
f.write(json.dumps(sorted_json, sort_keys=True, indent=4, separators=(',', ':')))
f.close()

