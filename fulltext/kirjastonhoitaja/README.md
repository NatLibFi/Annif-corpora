# "Kysy kirjastonhoitajalta" (Ask a librarian) question/answer corpus

This corpus contains 3150 Finnish language relatively short documents from
the service [Kysy kirjastonhoitajalta](https://www.kirjastot.fi/kysy) (Ask a
librarian). Each document is a question from the general public with an
answer from a librarian.

The corpus was extracted from the collection of over 25000 question/answer
pairs with the requirement that the document must have a minimum of 4
subjects.

The corpus has been split into the following directories:

* `all`: contains all the documents (N=3150)
* `train`: contains questions asked before 2016 (N=2625), intended for
  training
* `validate`: contains questions asked in 2016 (N=213), intended for
validating (e.g. choosing hyperparameters for a classifier)
* `test`: contains questions asked in 2017 (N=312), intended for final
evaluation
