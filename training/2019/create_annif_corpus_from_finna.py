# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#%%
# load current YSA
from rdflib import Graph
ysa = Graph()
ysa.parse('http://finto.fi/rest/v1/ysa/data?format=text/turtle')
#print(len(ysa))  # show number of triples


#%%
# load YSO 2019.3 Cicero
from rdflib import Graph
yso = Graph()
yso.parse('https://github.com/NatLibFi/Finto-data/raw/master/vocabularies/yso/releases/2019.3.Cicero/yso-skos.rdf', format='xml')
#print(len(yso))  # show number of triples


#%%
from rdflib import Literal, Namespace
from rdflib.namespace import SKOS, OWL

YSO = Namespace('http://www.yso.fi/onto/yso/')

def is_deprecated(ysouri):
    return (ysouri, OWL.deprecated, True) in yso

def label_to_yso_uri(label, lang):  
    value = Literal(label, lang)

    # first try YSA
    for prop in (SKOS.prefLabel, SKOS.altLabel):
        ysauri = ysa.value(None, prop, value, any=True)
        if ysauri is not None:
            # look up corresponding YSO URIs
            for matchprop in (SKOS.exactMatch, SKOS.closeMatch):
                matches = [str(match) for match in ysa.objects(ysauri, matchprop)
                           if match.startswith(YSO) and not is_deprecated(match)]
                if matches:
                    return matches
    
    # not found in YSA, try YSO instead
    for prop in (SKOS.prefLabel, SKOS.altLabel):
        uri = yso.value(None, prop, value, any=True)
        if uri is not None and not is_deprecated(uri):
            return [str(uri)]
    
    print("Unknown label '{}'".format(label), file=sys.stderr)
    return None


#print(label_to_yso_uri('kissa', 'fi'))  # YSO: kissa
#print(label_to_yso_uri('Ingmanin talo', 'fi')) # YSO: Casagranden talo
#print(label_to_yso_uri('siirtäminen', 'fi')) # YSO: siirto (liikuttaminen) + siirto (viestintä)
#print(label_to_yso_uri('Helsinki -- Kallio', 'fi'))  # YSO-paikat: Kallio (Helsinki)
#print(label_to_yso_uri('Zambia', 'fi'))  # YSO-paikat: Sambia
#print(label_to_yso_uri('not found', 'fi'))


#%%
import sys
import json


def main(ndjson_in):
    """Prints the title (nimike) and subjects (aiheet) contained in the json
    objects of the input."""
    for ind, line in enumerate(ndjson_in):
        line_dict = json.loads(line)
        if (
            not 'title' in line_dict.keys()
            or not 'subjectsExtended' in line_dict.keys()
        ):
            continue

        subjects = get_subjects(line_dict['subjectsExtended'])
        if subjects:
#            print(line_dict['title'] + '\t' + '\t'.join(subjects))
#            print(line_dict['title'] + '->' + '->'.join(subjects))
            print_title_with_subject_uris(line_dict['title'], subjects, 'fi')


def get_subjects(subject_dicts_in):
    """Returns a list of subjects, i.e. strings extracted from the heading
    fields of the dictionaries in the input list."""
    subjects_out = []
    for subject_dict in subject_dicts_in:
        if not ('source', 'ysa') in subject_dict.items():
            continue
        subjects_out.extend(
            [item for item in subject_dict['heading']]
        )
    return subjects_out


def print_title_with_subject_uris(title, subjects, lang):
    urilist = [label_to_yso_uri(label, lang) for label in subjects]
    urilist = [uri for uri in urilist if uri is not None]
    print(title + '\t' + '\t'.join(
         ['<'+item+'>' for sublist in urilist if sublist for item in sublist ]
    ))

#with open('finna-eng_test_1000_rows.ndjson') as fh:
#    main(fh)


#%%
if __name__ == '__main__':
    # QUESTION: Which way stdin is expected?
    if sys.stdin.isatty():  # When no redirected input from file
        # Print instructions and wait for input if not redirected input?
        print('No redirected stdin data from file found. '
              'Example usage with input and output data files:\n'
              '\t$ python extract_subjects.py < file_in.ndjson > file_out.tsv'
              '\n\nWaiting for input:')
        sys.exit()
    main(sys.stdin)
