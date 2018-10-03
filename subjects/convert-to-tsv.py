#!/usr/bin/env python3

# Convert and old-style (Annif prototype) subject corpus (a directory of
# *.txt files) into a new-style document-oriented corpus (a single TSV
# file).

import sys
import os
import os.path
import collections

if len(sys.argv) != 2:
    print("Usage: {} <directory> >corpus.tsv".format(sys.argv[0]),
          file=sys.stderr)
    sys.exit(1)

path = sys.argv[1]
if not os.path.isdir(path):
    print("Error: path '{}' is not a directory".format(path),
          file=sys.stderr)
    sys.exit(1)

doc_uris = collections.defaultdict(list)

for fn in os.listdir(path):
    with open(os.path.join(path, fn)) as f:
        uri, label = f.readline().strip().split(' ', 1)
        for line in f:
            doc_uris[line.strip()].append(uri)

for doc, uris in doc_uris.items():
    uricol = ' '.join(('<{}>'.format(uri) for uri in uris))
    print('{}\t{}'.format(doc, uricol))
