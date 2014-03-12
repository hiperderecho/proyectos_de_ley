#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string

def replace_tildes(x):
    tildes = {
                "á": "a",
                "é": "e",
                "í": "i",
                "ó": "o",
                "ú": "u",
                "ñ": "n",
                }
    if x in tildes:
        for k, v in tildes:
            print v
            x = string.replace(k, v, x)
        print "yes"
    return x

x = "á"
print replace_tildes(x).encode("utf8")

