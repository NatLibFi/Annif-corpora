#!/bin/bash

input=$1

base=${input%.ndjson.gz}

echo_stderr ()
{
    echo "$@" >&2
}


echo_stderr "input file: $input"
echo_stderr "output file basename: $base"

output=$base-fin.ndjson.gz
echo_stderr "extracting language fin to $output"
zgrep -F '"languages":["fin"]' $input | shuf | gzip >$output

output=$base-swe.ndjson.gz
echo_stderr "extracting language swe to $output"
zgrep -F '"languages":["swe"]' $input | shuf | gzip >$output

output=$base-eng.ndjson.gz
echo_stderr "extracting language eng to $output"
zgrep -F '"languages":["eng"]' $input | shuf | gzip >$output
