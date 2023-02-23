#!/usr/bin/env python3

import sys
from lxml import etree

#XMLParser = etree.XMLParser(remove_blank_text=True, recover=True, resolve_entities=False)
XMLParser = etree.XMLParser(remove_blank_text=True, recover=True, resolve_entities=False, huge_tree=True)

OAI_NAMESPACE = '{http://www.openarchives.org/OAI/%s/}' % '2.0'

with open(sys.argv[1]) as rec:
    xml = etree.XML(rec.read(), parser=XMLParser)
    element = xml.find('.//' + OAI_NAMESPACE + 'resumptionToken')
    print(element)
