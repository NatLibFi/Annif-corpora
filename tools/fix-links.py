#!/usr/bin/env python3
import os
import sys
from glob import glob

# Find broken links in a given directory and print those links. If given also
# a destination directory move the found links there, e.g.:
#./fix-links.py \
#	~/git/Annif-corpora-restricted/kirjaesittelyt/yso/fin/maui-train/ \
#   ~/git/Annif-corpora-restricted/kirjaesittelyt/yso/swe/maui-train/
#
# Meant for fixing in a wrong place after mv-txt-by-language.py

dirpath = sys.argv[1]
destdirpath = None
if len(sys.argv) == 3:
	destdirpath = sys.argv[2]

filepaths = glob(os.path.join(dirpath, '*'))

for filepath in filepaths:
	if os.path.islink(filepath) and not os.path.exists(filepath):
		filename = os.path.basename(filepath)
		if destdirpath is not None:
			destfilepath = os.path.join(destdirpath, filename)
			os.rename(filepath, destfilepath)
		else:
			print(filepath)
