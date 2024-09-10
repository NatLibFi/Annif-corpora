# Usage:
#
# python convert-corpus-yso-to-koko.py
#

import sys
import gzip

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


def convert(infile, outfile):
    for line in infile:
        if not '\t' in line:
            continue

        text, *yso_uris = line.split('\t')
        if not yso_uris:
            continue

        koko_uris = [yso_to_koko.get(yso_uri) for yso_uri in yso_uris]

        # Note: yso uris having not mapped in koko are skipped
        print(
            text
            + '\t'
            + ' '.join(
                ['<' + uri + '>' for uri in koko_uris if uri is not None]
            ),
            file=outfile
        )


yso_file_names = [
    'yso-finna-fi-01.tsv.gz',
    'yso-finna-fi-02.tsv.gz',
    'yso-finna-fi-03.tsv.gz',
    'yso-finna-fi-04.tsv.gz',
]

for ysofname in yso_file_names:
    kokofilename = ysofname.replace("yso-", "yso-to-koko-")
    with (
        gzip.open(ysofname, 'rt') as infile,
        gzip.open(kokofilename, 'wt') as outfile,
    ):
        convert(infile, outfile)
