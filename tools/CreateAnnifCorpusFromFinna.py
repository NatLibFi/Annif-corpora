#!/usr/bin/env python3
import gzip
import functools
import json
import sys
import unicodedata

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, OWL, DCTERMS, SKOS


# To convert to the final format:
# zcat finna-all-2020-02-swe.tsv.gz |shuf|gzip >yso-finna-sv.tsv.gz
# zcat finna-all-2020-02-eng.tsv.gz |shuf|gzip >yso-finna-en.tsv.gz
# The Finnish file must be split:
# zcat finna-all-2020-02-fin.tsv.gz |shuf|split -l 2000000 --numeric-suffixes=1 --additional-suffix=.tsv - yso-finna-fi-
# gzip yso-finna-fi-*.tsv


YSO = Namespace('http://www.yso.fi/onto/yso/')
COMPLAIN = False  # whether to complain about unknown labels
FINNA_BASE = 'finna-all-'


if len(sys.argv) < 2:
    print('No name of records batch provided.')
    sys.exit(1)
else:
    batch = sys.argv[1]


# load current YSA
ysa = Graph()
ysa.parse('http://finto.fi/rest/v1/ysa/data?format=text/turtle')
print('Number of triples in YSA: ', len(ysa))

# load current Allärs
allars = Graph()
allars.parse('http://finto.fi/rest/v1/allars/data?format=text/turtle')
print('Number of triples in Allärs: ', len(allars))

# load YSO and YSO Places
yso = Graph()
yso.parse('../vocab/yso-skos.ttl', format='turtle')
print('Number of triples in YSO+YSO Places: ', len(yso))


def is_deprecated(ysouri):
    return (ysouri, OWL.deprecated, True) in yso


def label_to_yso_uris(label, source, voc, lang, complain=COMPLAIN):
    #print("looking up '{}' from {} in language {}".format(label, source, lang))
    value = Literal(unicodedata.normalize('NFC', label), lang)

    for prop in (SKOS.prefLabel, SKOS.altLabel):
        vocuri = voc.value(None, prop, value, any=True)
        if vocuri is not None:
            if vocuri.startswith(YSO):
                return [vocuri]
            for matchprop in (SKOS.exactMatch, SKOS.closeMatch):
                matches = [match for match in voc.objects(vocuri, matchprop)
                           if match.startswith(YSO)]
                if matches:
                    return matches

    # hackish fallbacks for cases like "kulttuuri", where YSO Cicero is out of
    # date: look up via ysa/allars
    if source == 'yso/fin':
        matches = label_to_yso_uris(label, "ysa", ysa, lang)
        if matches:
            print("missing yso/fin label '{}' found via ysa".format(label))
            return matches

    if source == 'yso/swe':
        matches = label_to_yso_uris(label, "allars", allars, lang)
        if matches:
            print("missing yso/swe label '{}' found via allars".format(label))
            return matches

    if complain:
        print("Unknown label '{}' in source {}".format(label, source))
    return []


uris = label_to_yso_uris('kissa', 'yso/fin', yso, 'fi')  # YSO: kissa
print(uris)
assert URIRef('http://www.yso.fi/onto/yso/p19378') in uris
uris = label_to_yso_uris('Ingmanin talo', 'yso/fin', yso, 'fi')  # YSO: Casagranden talo
print(uris)
assert URIRef('http://www.yso.fi/onto/yso/p18095') in uris
uris = label_to_yso_uris('siirtäminen', 'ysa', ysa, 'fi')  # YSO: siirto
# 23.9.2020 No more YSO: siirto (liikuttaminen) + siirto (viestintä)
print(uris)
assert URIRef('http://www.yso.fi/onto/yso/p5700') in uris
uris = label_to_yso_uris('lähioikeudet', 'yso/fin', yso, 'fi')  # YSO: lähioikeudet
print(uris)
assert URIRef('http://www.yso.fi/onto/yso/p11910') in uris
uris = label_to_yso_uris('kulttuuri', 'yso/fin', yso, 'fi')  # YSO: kulttuuri
print(uris)
assert URIRef('http://www.yso.fi/onto/yso/p372') in uris
uris = label_to_yso_uris('Helsinki -- Kallio', 'ysa', ysa, 'fi')  # YSO-paikat: Kallio (Helsinki)
print(uris)
assert URIRef('http://www.yso.fi/onto/yso/p105606') in uris
uris = label_to_yso_uris('Zambia', 'yso/fin', yso, 'fi')  # YSO-paikat: Sambia
print(uris)
assert URIRef('http://www.yso.fi/onto/yso/p104983') in uris
uris = []
print(uris)
assert label_to_yso_uris('not found', 'yso/fin', yso, 'fi') == uris


@functools.lru_cache(maxsize=30000)
def replace_concept(uri):
    replacement_candidates = list(yso.objects(uri, DCTERMS.isReplacedBy)) + \
                             list(yso.objects(uri, SKOS.narrowMatch))
    replacements = [rc for rc in replacement_candidates if rc.startswith(YSO)]
    if len(replacements) == 0:
        return [uri]
    else:
        print("replacing", uri, "with", ' '.join([str(r) for r in replacements]))
        if len(replacements) > 1:
            print("warning: multiple replacements for", uri)
        return replacements


@functools.lru_cache(maxsize=30000)
def check_concept(uri):
    if (uri, RDF.type, SKOS.Concept) not in yso:
        print(str(uri), "not a skos:Concept")
        return False
    if yso.value(uri, OWL.deprecated, None, any=True):
        print(str(uri), "is deprecated")
        return False
    return True


replaced = replace_concept(URIRef('http://www.yso.fi/onto/yso/p23766'))  # should be replaced by p1947 and p22036
assert len(replaced) == 2
assert URIRef('http://www.yso.fi/onto/yso/p1947') in replaced
assert URIRef('http://www.yso.fi/onto/yso/p22036') in replaced

assert not check_concept(URIRef('http://www.yso.fi/onto/yso/p23766'))  # is deprecated, should return False

        
def get_subject_uris(subject_dicts_in):
    """Returns a list of subjects, i.e. strings extracted from the heading
    fields of the dictionaries in the input list."""

    subjects_out = []
    for subject_dict in subject_dicts_in:
        if ('source', 'ysa') in subject_dict.items():
            source = 'ysa'
            voc = ysa
            lang = 'fi'
        elif ('source', 'allars') in subject_dict.items():
            source = 'allars'
            voc = allars
            lang = 'sv'
        elif ('source', 'yso/fin') in subject_dict.items():
            source = 'yso/fin'
            voc = yso
            lang = 'fi'
        elif ('source', 'yso/fin') in subject_dict.items():
            source = 'yso/swe'
            voc = yso
            lang = 'sv'
        else:
            continue
        
        uris = []
        
        if len(subject_dict['heading']) > 1:
            label = ' -- '.join(subject_dict['heading'])
            uris = label_to_yso_uris(label, source, voc, lang, complain=False)

        if not uris:
            # not found as a precoordinated subject, try the individual parts instead
            uris = []
            for label in subject_dict['heading']:
                uris.extend(label_to_yso_uris(label, source, voc, lang))
        
        for uri in uris:
            newuris = replace_concept(uri)
            for newuri in newuris:
                if check_concept(newuri):
                    subjects_out.append(newuri)

    return set(subjects_out)


def main(ndjson_in, output):
    """Prints the title (nimike) and subjects (aiheet) contained in the json
    objects of the input."""
    for ind, line in enumerate(ndjson_in):
        line_dict = json.loads(line)
        if 'title' not in line_dict:
            continue
        if 'subjectsExtended' not in line_dict:
            continue

        subjects = get_subject_uris(line_dict['subjectsExtended'])
        if subjects:
            print(line_dict['title'] + '\t' + '\t'.join(
                (str(subj)for subj in subjects)), file=output)


# inputfile = 'finna-metadata-sample-10k.ndjson'
# with open(inputfile, 'rt') as inputf:
#     with gzip.open(''.join(inputfile.split('.')[:-1]) + '.tsv.gz', 'wt') as outputf:
#         main(inputf, outputf)

with gzip.open(FINNA_BASE + batch + '-swe.ndjson.gz', 'rt') as inputf:
    with gzip.open(FINNA_BASE + batch + '-swe.tsv.gz', 'wt') as outputf:
        main(inputf, outputf)

with gzip.open(FINNA_BASE + batch + '-eng.ndjson.gz', 'rt') as inputf:
    with gzip.open(FINNA_BASE + batch + '-eng.tsv.gz', 'wt') as outputf:
        main(inputf, outputf)

with gzip.open(FINNA_BASE + batch + '-fin.ndjson.gz', 'rt') as inputf:
    with gzip.open(FINNA_BASE + batch + '-fin.tsv.gz', 'wt') as outputf:
        main(inputf, outputf)
