#!/usr/bin/env python3
import sys
import cld3
"""
Filters out (parts of) Finna records given via stdin that are in a different
language than specified by language code given as argument. "=" sign is used as
the delimeter in splitting parts.

For example:
zcat yso-finna-en.tsv.gz | ./lang-filter-records.py en > yso-finna-en-filt.tsv
"""


if len(sys.argv) < 2:
    print('No language code provided.')
    sys.exit(1)
else:
    lang = sys.argv[1]

for line in sys.stdin:
    text, uris = line.split('\t', maxsplit=1)
    if '=' in text:
        parts = text.split('=')
    else:
        parts = [text]

    retained_parts = []
    for part in parts:
        lang_info = cld3.get_language(part.strip())
        if lang_info.language == lang or not lang_info.is_reliable \
                or lang_info.probability < 0.99:
            retained_parts.append(part)
        else:
            print('FILTERED OUT: "', part.strip(), '"\t', lang_info,
                  sep='', file=sys.stderr)

    if not retained_parts:
        continue
    print(' '.join(retained_parts), uris, sep='\t', end='')
