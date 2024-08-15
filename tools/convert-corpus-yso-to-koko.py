# Usage:
#
# zcat yso-finna-fi-01.tsv.gz | python convert-corpus-yso-to-koko.py | gzip > yso-to-koko-finna-fi-01.tsv.gz
#

import sys

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, OWL, DCTERMS, SKOS


KOKO = Namespace('http://www.yso.fi/onto/koko/')
YSO = Namespace('http://www.yso.fi/onto/yso/')


# load KOKO
koko_path = "/data/Annif-corpora/vocab/koko-skos.ttl"
koko = Graph()
koko.parse(koko_path, format='turtle')
# print('Number of triples in KOKO: ', len(koko))


# Create an index for YSO to KOKO mappings
yso_to_koko = {}
for s, p, o in koko.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#exactMatch"), None)):
    if o.startswith(YSO):
        yso_to_koko[str(o)] = str(s)
# print('Number of entries in YSO-to-KOKO mapping: ', len(yso_to_koko))

assert yso_to_koko['http://www.yso.fi/onto/yso/p6182'] == 'http://www.yso.fi/onto/koko/p5300'  # Lääkärit


for line in sys.stdin:
    if not '\t' in line:
        continue

    text, *yso_uris = line.split('\t')

    koko_uris = [yso_to_koko.get(yso_uri) for yso_uri in yso_uris]
    # Note: yso uris having not mapped in koko are skipped
    print(
        text
        + '\t'
        + '\t'.join(
            [uri for uri in koko_uris if uri is not None]
        )
    )
