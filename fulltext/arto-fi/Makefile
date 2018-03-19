# Rules for fetching and converting documents

all: pdf txt

pdf: $(patsubst %.url,%.pdf,$(wildcard all/*.url))

%.pdf: %.url
	wget -q --no-use-server-timestamps -O $@ `cat $<` || rm -f $@

txt: $(patsubst %.url,%.txt,$(wildcard all/*.url))

%.txt: %.pdf
	pdftotext $<

.PHONY: all pdf
