# Makupalat corpus

This corpus is based on the [Makupalat](https://www.makupalat.fi/) link
collection maintained by Finnish public libraries. Each document is formed
from the title and descriptive text of a link and labeled with one or more
classes from the [Finnish Public Libraries Classification
System](https://finto.fi/ykl/) (a.k.a. YKL, a decimal classification system
based on DDC). The total number of documents is 16350. The corpus was
created from a database dump created in April 2018. Only Finnish language
documents were extracted.

The corpus has been divided into the following subsets:

* `train`: links created before 2016 (N=15361)
* `validate`: links created during 2016 (N=435)
* `test`: links created after 2016 (N=554)
