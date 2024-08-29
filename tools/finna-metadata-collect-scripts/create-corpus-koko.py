#!/usr/bin/env python3
import gzip
import functools
import json
import sys
import unicodedata

from datetime import datetime
from collections import defaultdict
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, OWL, DCTERMS, SKOS
from simplemma.language_detector import langdetect


# Create the input file with the command:
# zgrep "\\\/onto\\\/koko" finna-all-YYYY-MM-DD.ndjson.gz | gzip > finna-koko-YYYY-MM-DD-with-koko-uris.ndjson.gz


KOKO = Namespace('http://www.yso.fi/onto/koko/')
YSO = Namespace('http://www.yso.fi/onto/yso/')

COMPLAIN = True  # whether to complain about unknown labels
FINNA_BASE = 'finna-all-'

MIN_SUBJECTS = 4

TESTSET_BEGIN_YEAR = 2024  # Compared to first_indexed timestamp
TESTSET_FORMATS = {
    "image": "0/Image/",
    "physicalobject": "0/PhysicalObject/",
    "workofart": "0/WorkOfArt/",
}  # TODO Add rakennukset, ehkä "image": "0/Image/", type: arkistomateriaali
MAX_TEST_RECORDS = 3000


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


# Create an index for YSO to KOKO mappings
yso_to_koko = {}
for s, p, o in koko.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#exactMatch"), None)):
    if o.startswith(YSO):
        yso_to_koko[o] = s
print('Number of entries in YSO-to-KOKO mapping: ', len(yso_to_koko))

assert str(yso_to_koko[URIRef('http://www.yso.fi/onto/yso/p6182')]) == 'http://www.yso.fi/onto/koko/p5300'  # Lääkärit


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
    if uri is None:
        return []
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
        elif "id" in subject_dict.keys() and subject_dict["id"].startswith(YSO):
            yso_uri = subject_dict["id"]
            koko_uri = yso_to_koko.get(URIRef(yso_uri))
            uris = [koko_uri]  # if koko_uri != "None" else []
        else:
            continue

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

    return set(subjects_out)


def is_testset_member(rec):
    if rec['first_indexed'] is None:
        return False
    dt = datetime.strptime(rec['first_indexed'], '%Y-%m-%dT%H:%M:%SZ')
    if dt.year >= TESTSET_BEGIN_YEAR:
        return True
    return False


def read_timestamps():
    ts_filename = 'finna-with-koko-uris-first-indexed-timestamps.ndjson.gz'
    timestamps = {}
    with gzip.open(ts_filename, 'rt') as ts_file:
        for ind, line in enumerate(ts_file):
            ts_record = json.loads(line)
            timestamps.update(ts_record)
    return timestamps


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


def detect_language(text):
    results = langdetect(text, lang=('fi', 'sv', 'en'))
    if not results:
        return None
    elif results[0][1] < 0.05:  # accuracy threshold
        return None
    return results[0][0]


rec_type_counter = defaultdict(int)


def choose_testset_type(format):
    global rec_type_counter

    if rec_type_counter[format] >= MAX_TEST_RECORDS:
        return None
    if rec_type_counter["other"] >= MAX_TEST_RECORDS:
        return None

    rec_type_counter[format] += 1
    if format == TESTSET_FORMATS["image"]:
        return testimagesf
    elif format == TESTSET_FORMATS["workofart"]:
        return testartsf
    elif format == TESTSET_FORMATS["physicalobject"]:
        return testphysobjectsf

    rec_type_counter["other"] += 1
    return testotherf


def print_record(line_dict, subjects, ind):
    # if title == '' and summary == '':
    #     return

    # year = int(line_dict["publicationDates"][0]) if line_dict["publicationDates"] else -1  # TODO Is picking first element ok?
    format = line_dict["formats"][0]["value"] if line_dict["formats"] else ""  # TODO Is picking first element ok?

    title = line_dict['title']
    summary = line_dict['summary'][0] if len(line_dict['summary']) == 1 else ''
    text = cleanup(title + ' ¤ ' + summary)

    if is_printed(title, subjects):
        return
    if is_printed(summary, subjects):
        return

    if len(subjects) < MIN_SUBJECTS:
        return

    lang = detect_language(text)
    if lang != 'fi':
        print(f"Not Finnish: {text[:500]}")
        return

    if is_testset_member(line_dict):
        file = choose_testset_type(format)
    else:
        file = trainf

    if file is None:
        return

    print(
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
            line_dict["first_indexed"] = first_indexed_ts[line_dict["id"]]
            print_record(line_dict, subjects, ind)
        elif COMPLAIN:
            print(f'Line {ind}: No subjects found')


first_indexed_ts = read_timestamps()

print('Processing records')
with gzip.open(FINNA_BASE + batch + '-with-koko-uris.ndjson.gz', 'rt') as inputf:
    with (
        gzip.open('finna-koko-train.tsv.gz', 'wt') as trainf,
        gzip.open('finna-koko-test-images.tsv.gz', 'wt') as testimagesf,
        gzip.open('finna-koko-test-physobjects.tsv.gz', 'wt') as testphysobjectsf,
        gzip.open('finna-koko-test-arts.tsv.gz', 'wt') as testartsf,
        gzip.open('finna-koko-test-others.tsv.gz', 'wt') as testotherf,
    ):
        main(inputf)
