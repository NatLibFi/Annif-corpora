#!/usr/bin/env python3
import sys
import os
import cld3
from glob import glob

# Find txt files in a given directory of a given language (code) and print the
# content. If given also a destination directory move the found txt files and
# the corresponding tsv files there, e.g. for all docs in Swedish:
#
# ./mv-txts-by-language.py \
#    ~/git/Annif-corpora-restricted/kirjaesittelyt/yso/fin/validate/ \
#    sv \
#    ~/git/Annif-corpora-restricted/kirjaesittelyt/yso/swe/validate/
#
# This leaves links pointing to the moved files broken, fix those by moving
# also the links fix-links.py.


dirpath = sys.argv[1]
lang = sys.argv[2]
destdirpath = None

if len(sys.argv) == 4:
    destdirpath = sys.argv[3]

txtfilepaths = glob(os.path.join(dirpath, '*.txt'))

for txtfilepath in txtfilepaths:
    with open(txtfilepath, 'r') as file:
        text = file.read()
    lan_info = cld3.get_language(text)

    if lan_info.language == lang:
        print('-'*len(txtfilepath))
        print(txtfilepath)
        print(text)
        print(lan_info)
        print()
        if destdirpath is not None:
            txtfilename = os.path.basename(txtfilepath)
            destfilepath = os.path.join(destdirpath, txtfilename)
            os.rename(txtfilepath, destfilepath)

            tsvfilename = txtfilename.replace('.txt', '.tsv')
            tsvfilepath = txtfilepath.replace('.txt', '.tsv')
            destfilepath = os.path.join(destdirpath, tsvfilename)
            os.rename(tsvfilepath, destfilepath)
