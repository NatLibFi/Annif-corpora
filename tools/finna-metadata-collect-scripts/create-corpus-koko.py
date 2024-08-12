#!/usr/bin/env python3
import gzip
import functools
import json
import sys
import unicodedata

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, OWL, DCTERMS, SKOS


KOKO = Namespace('http://www.yso.fi/onto/koko/')
COMPLAIN = True  # whether to complain about unknown labels
FINNA_BASE = 'finna-all-'

# TESTSET_BEGIN_YEAR = 0  # There is not publicationDates in most records, need
# to do test/train split other way
TESTSET_FRACTION = 0.1
TESTSET_FORMATS = {
    "image": "0/Image/",
    "physicalobject": "0/PhysicalObject/",
    "workofart": "0/WorkOfArt/",
}  # TODO Add rakennukset, ehkä "image": "0/Image/", type: arkistomateriaali
# Kuvat, esineet, rakennukset ja taideteokset erikseen (tai esineet + taideteokset samassa nipussa


if len(sys.argv) != 3:
    print('''Not enough arguments. Usage:
	./create-corpus-koko.py BATCH PATH_TO_ONTOLOGY''')
    sys.exit(1)
else:
    batch = sys.argv[1]
    koko_path = sys.argv[2]

# load KOKO
koko = Graph()
koko.parse(koko_path, format='turtle')
print('Number of triples in KOKO: ', len(koko))


def label_to_uris(label, voc, lang, complain=COMPLAIN):
    #print("looking up '{}' from {} in language {}".format(label, source, lang))
    # Remove trailing "." present in labels of some records
    value = Literal(unicodedata.normalize('NFC', label.rstrip('.')), lang)

    for prop in (SKOS.prefLabel, SKOS.altLabel):
        vocuri = voc.value(None, prop, value, any=True)
        if vocuri is not None:
            if vocuri.startswith(KOKO):
                return [vocuri]
            for matchprop in (SKOS.exactMatch, SKOS.closeMatch):
                matches = [match for match in voc.objects(vocuri, matchprop)
                           if match.startswith(YSO)]
                if matches:
                    return matches
    if complain:
        print("Unknown label '{}'".format(label))
    return []

uris = label_to_uris('kissa', koko, 'fi')  # YSO: kissa
print(uris)
assert URIRef('http://www.yso.fi/onto/koko/p37252') in uris
uris = label_to_uris('Ingmanin talo', koko, 'fi')  # Casagranden talo
print(uris)
assert URIRef('http://www.yso.fi/onto/koko/p62854') in uris
# uris = label_to_uris('siirtäminen', 'ysa', ysa, 'fi')  # YSO: siirto
# 23.9.2020 No more YSO: siirto (liikuttaminen) + siirto (viestintä)
#print(uris)
# assert URIRef('http://www.yso.fi/onto/yso/p5700') in uris
uris = label_to_uris('lähioikeudet', koko, 'fi')  # lähioikeudet
print(uris)
assert URIRef('http://www.yso.fi/onto/koko/p11360') in uris
uris = label_to_uris('kulttuuri', koko, 'fi')  # kulttuuri
print(uris)
assert URIRef('http://www.yso.fi/onto/koko/p31131') in uris
# uris = label_to_uris('Helsinki -- Kallio', 'ysa', ysa, 'fi')  # YSO-paikat: Kallio (Helsinki)
# #print(uris)
# assert URIRef('http://www.yso.fi/onto/yso/p105606') in uris
# uris = label_to_uris('Zambia', koko, 'fi')  # YSO-paikat: Sambia
# #print(uris)
# assert URIRef('http://www.yso.fi/onto/yso/p104983') in uris
uris = []
print(uris)
assert label_to_uris('not found', koko, 'fi') == uris


@functools.lru_cache(maxsize=30000)
def replace_concept(uri):
    replacement_candidates = list(koko.objects(uri, DCTERMS.isReplacedBy)) + \
                             list(koko.objects(uri, SKOS.narrowMatch))
    replacements = [rc for rc in replacement_candidates if rc.startswith(KOKO)]
    if len(replacements) == 0:
        return [uri]
    else:
        print("replacing", uri, "with", ' '.join([str(r) for r in replacements]))
        if len(replacements) > 1:
            print("warning: multiple replacements for", uri)
        return replacements


@functools.lru_cache(maxsize=30000)
def check_concept(uri):
    if (uri, RDF.type, SKOS.Concept) not in koko:
        print(str(uri), "not a skos:Concept")
        return False
    if koko.value(uri, OWL.deprecated, None, any=True):
        print(str(uri), "is deprecated")
        return False
    return True


# TODO
assert check_concept(URIRef('http://www.yso.fi/onto/koko/p5300'))  # Lääkärit
# replaced = replace_concept(URIRef('http://www.yso.fi/onto/yso/p23766'))  # should be replaced by p1947 and p22036
# print(len(replaced))
# print(replaced)
# assert len(replaced) == 2
# assert URIRef('http://www.yso.fi/onto/yso/p1947') in replaced
# assert URIRef('http://www.yso.fi/onto/yso/p22036') in replaced

# assert not check_concept(URIRef('http://www.yso.fi/onto/yso/p23766'))  # is deprecated, should return False


def get_subject_uris(subject_dicts_in):
    """Returns a list of subjects, i.e. strings extracted from the heading
    fields of the dictionaries in the input list."""

    subjects_out = []
    for subject_dict in subject_dicts_in:
        if "id" in subject_dict.keys() and subject_dict["id"].startswith(KOKO):
            uris = [subject_dict["id"]]
            # print(uris)
        else:
            continue

        # uris = []

        # TODO
        # if len(subject_dict['heading']) > 1:
        #     label = ' -- '.join(subject_dict['heading'])
        #     uris = label_to_uris(label, source, voc, lang, complain=False)

        # if not uris:
        #     # not found as a precoordinated subject, try the individual parts instead
        #     uris = []
        #     for label in subject_dict['heading']:
        #         uris.extend(label_to_uris(label, source, voc, lang))

        for uri in uris:
            newuris = replace_concept(uri)
            for newuri in newuris:
                # print(newuri)
                if check_concept(URIRef(newuri)):
                    subjects_out.append(newuri)

    # print(set(subjects_out))
    return set(subjects_out)


def is_testset_member(text):
    return hash(text) % 100 < int(TESTSET_FRACTION * 100)

def cleanup(text):
    return " ".join(text.split())


printed = set()


def is_printed(text, subjects):
    global printed

    current = hash((text, tuple(subjects)))
    if current in printed:
        return True
    printed.add(current)
    return False


def print_record(line_dict, subjects, ind):
    # if title == '' and summary == '':
    #     return

    # year = int(line_dict["publicationDates"][0]) if line_dict["publicationDates"] else -1  # TODO Is picking first element ok?
    format = line_dict["formats"][0]["value"] if line_dict["formats"] else ""  # TODO Is picking first element ok?

    title = line_dict['title']
    summary = line_dict['summary'][0] if len(line_dict['summary']) == 1 else ''
    text = cleanup(title + ' ¤ ' + summary)

    if is_printed(text, subjects):
        return

    if is_testset_member(text):
        if format == TESTSET_FORMATS["image"]:
            file = testimagesf
        elif format == TESTSET_FORMATS["workofart"]:
            file = testartsf
        elif format == TESTSET_FORMATS["physicalobject"]:
            file = testphysobjectsf
        # elif format in ("0/Book/", "0/OtherText/", "0/Document/"):
            # print(f"known train: {format}")
            # file = testotherf
        else:
            # print(f'unknown format for testset: {line_dict["formats"]}')
            file = testotherf
    else:
        file = trainf

    print(
        # ' ¤ '.join((title, summary))
        text
        + '\t'
        + '\t'.join(
            (str(subj)for subj in subjects)
    ), file=file)


def main(ndjson_in):
    """Prints the title (nimike) and subjects (aiheet) contained in the json
    objects of the input."""
    for ind, line in enumerate(ndjson_in):
        line_dict = json.loads(line)
        if 'title' not in line_dict:
            if COMPLAIN:
                print(f'Line {ind}: No title')
            continue
        if line_dict['title'].strip() == '':
            if COMPLAIN:
                print(f'Line {ind}: Empty title')
            continue
        if 'subjectsExtended' not in line_dict:
            if COMPLAIN:
                print(f'Line {ind}: No subjectsExtended')
            continue

        subjects = get_subject_uris(line_dict['subjectsExtended'])
        if subjects:
            print_record(line_dict, subjects, ind)
        elif COMPLAIN:
            print(f'Line {ind}: No subjects found')


print('Processing records')
with gzip.open(FINNA_BASE + batch + '-with-koko-uris.ndjson.gz', 'rt') as inputf:
    with (
        gzip.open('koko-train.tsv.gz', 'wt') as trainf,
        gzip.open('koko-test-images.tsv.gz', 'wt') as testimagesf,
        gzip.open('koko-test-physobjects.tsv.gz', 'wt') as testphysobjectsf,
        gzip.open('koko-test-arts.tsv.gz', 'wt') as testartsf,
        gzip.open('koko-test-others.tsv.gz', 'wt') as testotherf,
    ):
        main(inputf)


# print('Processing Swedish records')
# with gzip.open(FINNA_BASE + batch + '-with-koko-uris-swe.ndjson.gz', 'rt') as inputf:
#     with gzip.open(FINNA_BASE + batch + '-with-koko-uris-swe.tsv.gz', 'wt') as outputf:
#         main(inputf, outputf)

# print('Processing English records')
# with gzip.open(FINNA_BASE + batch + '-with-koko-uris-eng.ndjson.gz', 'rt') as inputf:
#     with gzip.open(FINNA_BASE + batch + '-with-koko-uris-eng.tsv.gz', 'wt') as outputf:
#         main(inputf, outputf)

# print('Processing Finnish records')
# with gzip.open(FINNA_BASE + batch + '-with-koko-uris-fin.ndjson.gz', 'rt') as inputf:
#     with gzip.open(FINNA_BASE + batch + '-with-koko-uris-fin.tsv.gz', 'wt') as outputf:
#         main(inputf, outputf)
