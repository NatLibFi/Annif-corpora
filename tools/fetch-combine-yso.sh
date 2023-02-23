#!/bin/bash

cd ../yso

curdate=`date +"%Y-%m-%d"`

# fetch current YSO and YSO Places from Finto API
wget -q https://api.finto.fi/rest/v1/yso/data -O yso.ttl
wget -q https://api.finto.fi/rest/v1/yso-paikat/data -O yso-paikat.ttl

# combine them into a single Turtle file
rdfpipe -o turtle yso.ttl yso-paikat.ttl >yso-combined-$curdate.ttl
