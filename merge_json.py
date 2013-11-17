# -*- coding: utf-8 -*-

import codecs
import json
import sys

if len(sys.argv) < 2:
    print "This script merges two json files"
    print "command.py jsonFile NewJsonFile output"
    sys.exit()

f = codecs.open(sys.argv[1].strip(), "r", "utf-8")
input_json = json.loads(f.read())
f.close()

f = codecs.open(sys.argv[2].strip(), "r", "utf-8")
input_json_new = json.loads(f.read())
f.close()

for i in input_json_new:
    if i not in input_json:
        input_json.append(i)

sorted_json = sorted(input_json, reverse=True)

f = codecs.open(sys.argv[3].strip(), "w", "utf-8")
f.write(json.dumps(sorted_json, sort_keys=True, indent=4, separators=(',', ':')))
f.close()

print "The files were merged, sorted and written to file %s" % str(sys.argv[3].strip())
