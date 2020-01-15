# Wikidata + Wikipedia corpus

This directory contains a training corpus for Annif based on Wikidata and
English Wikipedia. The idea is to extract the Wikidata entities which have
at least 40 sitelinks, including English Wikipedia, and then create a corpus
combining the Wikipedia texts (the input text) and Wikidata entities/URIs
(the subject). With a corpus like this, it is possible to predict the most
relevant Wikidata URIs (among the subset that was selected) for any input text.

Sources used:

* Wikidata "truthy" dump dated 2018-11-18
* English Wikipedia text dump dated 2018-11-25

The corpus contains 50531 Wikidata entities (with corresponding Wikipedia
text) that matched the above criteria.

# Suggested Annif project configuration

This corpus works OK with the TFIDF backend in Annif. Since there is only
one example/document per subject/URI, it may not work so well with other
algorithms that expect many examples per subject.

```
[wikidata-en]
name=Wikidata TF-IDF English
language=en
backend=tfidf
analyzer=snowball(english)
limit=100
vocab=wikidata-en
```

# Licensing

The Wikidata dump is CC0 licensed and published by Wikimedia.

The Wikipedia dump is based on text of Wikipedia articles contributed by
individual authors around the world. It was published by the Wikimedia
Foundation and is licensed under the [GNU Free Documentation License
](https://www.wikipedia.org/wiki/Wikipedia:Copyrights) (GFDL) and the
[Creative Commons Attribution-Share-Alike
3.0](https://creativecommons.org/licenses/by-sa/3.0/) License.

Since this corpus is derived from the Wikidata and Wikipedia dumps, the same
GFDL+CC-SA-3.0 licensing applies also to this corpus.
