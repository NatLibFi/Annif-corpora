# Rules for fetching and converting documents

all: pdf txt

pdf: $(patsubst %.url,%.pdf,$(wildcard */*.url))

%.pdf: %.url
	wget -q --no-use-server-timestamps -O $@ `cat $<` || rm -f $@

txt: $(patsubst %.url,%.txt,$(wildcard */*.url))

%.txt: %.pdf
	pdftotext $<

.PHONY: all pdf txt

