#!/bin/bash

set -e

. venv/bin/activate

# Create corpus from raw Finna records using YSO+YSO-places vocabulary
./create-corpus.py $1 ../Annif-corpora/vocab/yso-skos.ttl > create-corpus-$1.log

# Shuffle record order, split Finnish records into three files
zcat finna-all-$1-eng.tsv.gz |shuf|gzip >yso-finna-en.tsv.gz
zcat finna-all-$1-swe.tsv.gz |shuf|gzip >yso-finna-sv.tsv.gz
zcat finna-all-$1-fin.tsv.gz |shuf|split -l 2000000 --numeric-suffixes=1 --additional-suffix=.tsv - yso-finna-fi-; gzip --force yso-finna-fi-*.tsv
