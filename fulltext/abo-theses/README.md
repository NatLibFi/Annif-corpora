# Theses from Åbo Akademi University

This directory contains a corpus of ca. 1100 Master's and Licentiate theses
in Swedish and English language published in the years 2020 to 2022,
collected from the [Åbo Akademi University digital
repository](https://www.doria.fi/handle/10024/87831) which forms a part of
the Doria repository.

Only the URLs and subject metadata are stored in this Git repository. Actual
PDF documents must be downloaded separately.

## Retrieving the PDFs

You can fetch the PDF files using the Makefile:

    make pdf

This requires the `wget` utility. To download more than one document at a time,
add the `-jN` option, where `N` specifies is the number of jobs to run
simultaneously (e.g. `make -j8 pdf` will download 8 documents in parallel).

## Converting the PDFs to text

You can convert the fetched PDF files to text files using the Makefile:

    make txt

This requires the `pdftotext` utility. To convert more than one document at a time,
add the `-jN` option, where `N` specifies is the number of jobs to run
simultaneously (e.g. `make -j4 txt` will convert 4 documents in parallel).
