This directory contains a small (toy) Annif corpus consisting of characters
from the Harry Potter novels categorized according to the four houses in
Hogwarts.

The information has been collected from the Muggles' Guide to Harry
Potter:

https://en.m.wikibooks.org/wiki/Muggles%27_Guide_to_Harry_Potter/Characters

Suggested project configuration:

```
[hogwarts]
name=Hogwarts Houses
language=en
analyzer=simple
backend=fasttext
vocab=hogwarts
limit=4
dim=100
lr=0.25
epoch=100
loss=softmax
chunksize=1000
minn=1
maxn=4
minCount=3
```
