#!/bin/bash

. venv/bin/activate

curdate=`date +"%Y-%m-%d"`

# collect all the records from Finna
./collect.py 2>collect-$curdate.log | gzip >finna-all-$curdate.ndjson.gz

# filter by language into separate -fin, -swe and -eng files
./filter-by-language.sh finna-all-$curdate.ndjson.gz 2>filter-$curdate.log

# upload to huggingface hub and tag
hf upload NatLibFi/Finna-metadata finna-all-$curdate.ndjson.gz /metadata.jsonl.gz --repo-type=dataset --commit-message "Upload harvest $curdate"
hf repo tag create NatLibFi/Finna-metadata $curdate --repo-type=dataset
