This directory contains subject vocabularies to support Annif models.

# General Finnish Ontology YSO

The [General Finnish Ontology
YSO](https://www.kansalliskirjasto.fi/en/services/expert-services-of-data-description/general-finnish-ontology-yso)
is a multilingual subject vocabulary.  It is available in three languages:
Finnish, Swedish and English.

## SKOS files

The file [yso-skos-boethius.rdf](yso-skos-boethius.rdf) is a version of YSO
(2018.3 Boethius) released in March 2018.  The SKOS file in this repository
is simply converted to RDF/XML from the [original Turtle
file](https://github.com/NatLibFi/Finto-data/tree/master/vocabularies/yso/releases/2018.3.Boethius)
using the `rapper` tool, because Maui (as of version 1.4.5) requires RDF/XML
syntax.

## TSV files

The `yso-*.tsv` files contain the concepts (URIs and preferred labels) of
YSO in a [simple TSV
format](https://github.com/NatLibFi/Annif/wiki/Subject-vocabulary-formats)
supported by Annif.

This version of YSO dates from March 2017 and is the
same version used to build the yso-finna document corpora under the
[training](../training/) directory.

## License information

YSO is copyrighted by National Library of Finland, Semantic Computing
Research Group (SeCo) and The Finnish Terminology Centre TSK. It is
republished here according to the CC By 4.0 license.
