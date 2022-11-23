#!/bin/bash

. venv/bin/activate

curdate=`date +"%Y-%m-%d"`

# collect all the records from Finna
./collect.py 2>collect-$curdate.log | gzip >finna-all-$curdate.ndjson.gz

# filter by language into separate -fin, -swe and -eng files
./filter-by-language.sh finna-all-$curdate.ndjson.gz 2>filter-$curdate.log
