# Rules for fetching and converting documents

all: pdf

pdf: $(patsubst %.url,%.pdf,$(wildcard *.url))

%.pdf: %.url
	wget -q --no-use-server-timestamps -O $@ `cat $<` || rm -f $@


.PHONY: all pdf
