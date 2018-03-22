# Theses from University of Jyväskylä

This directory contains a corpus of 7400 Master's and doctoral theses
published in the years 2010 to 2017, collected from the [University of
Jyväskylä digital repository](https://jyx2.jyu.fi).

Only the URLs and subject metadata are stored in this Git repository. Actual
PDF documents must be downloaded separately.

## Retrieving the PDFs

You can fetch the PDF files using the Makefile:

    make pdf

This requires the `wget` utility.

## Converting the PDFs to text

You can convert the fetched PDF files to text files using the Makefile:

    make txt

This requires the `pdftotext` utility.
