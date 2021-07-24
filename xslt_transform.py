#!/usr/bin/python
import lxml.etree as et
import sys
USAGE = sys.argv[0] + " <template> <doc>"
if len(sys.argv) < 3:
    print (USAGE)
    sys.exit(-1)
template_path = sys.argv[1]
doc_path = sys.argv[2]
template_dom = et.parse(template_path)
doc_dom = et.parse(doc_path)
transform = et.XSLT(template_dom)
transfomed_dom = transform(doc_dom)
print(et.tostring(transfomed_dom, pretty_print=True))