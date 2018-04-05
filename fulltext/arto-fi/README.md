# Finnish language articles from Arto database

This corpus contains 6287 Finnish language articles extracted from the Arto
database. The articles themselves are not stored in the repository, but must
be fetched separately from the URLs stored in `.url` files.

## Retrieving the PDFs

You can fetch the PDF files using the Makefile:

    make pdf

This requires the `wget` utility. However, most of the files are located on the
[Elektra](http://elektra.helsinki.fi/) service which restricts access to
Finnish universities and public libraries.

## Converting the PDFs to text

You can convert the fetched PDF files to text files using the Makefile:

    make txt

This requires the `pdftotext` utility.

## Sub-corpora

The corpus has been split randomly into the following directories.
Directories other than `all` consist of symlinks to the `all` directory.

* `all`: contains all the documents (N=6287)
* `train`: contains 5287 documents intended for training
* `validate`: contains 500 documents intended for validating (e.g. choosing 
hyperparameters for a classifier)
* `test`: contains 500 documents intended for final evaluation
