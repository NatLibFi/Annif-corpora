#!/usr/bin/env python3

import traceback
import time
import sys
import sickle
from lxml import etree

# monkey patch sickle.response to handle large XML responses
# by enabling the huge_tree option (aka XML_PARSE_HUGE)

sickle.response.XMLParser = etree.XMLParser(remove_blank_text=True,
                                            recover=True,
                                            resolve_entities=False,
                                            huge_tree=True)

headers = {
    'User-Agent': 'Annif-Finna-collect'
}

sickle = sickle.Sickle('https://api.finna.fi/OAI/Server', headers=headers)

if len(sys.argv) > 1:
    current_token = sys.argv[1]
else:
    current_token = None

while True:
    params = { 	'metadataPrefix': 'oai_finna_json',
                'set': 'non_dedup',
                'timeout': 30 }

    if current_token is not None:
        params['resumptionToken'] = current_token

    try:
        print("Performing call with params {}".format(params), file=sys.stderr)
        records = sickle.ListRecords(**params)

        for idx, rec in enumerate(records):
            if records.resumption_token:
                token = records.resumption_token.token
                if token != current_token:
                    print("Resumption token: {} expires: {}".format(token, records.resumption_token.expiration_date), file=sys.stderr)
                    current_token = token
            else:
                print("No resumption token in response", file=sys.stderr)
                print(records.oai_response.raw, file=sys.stderr)
                current_token = None
            if 'metadata' in rec.metadata and len(rec.metadata['metadata']) > 0:
                json_data = rec.metadata['metadata'][0]
                print(json_data)
        
        if current_token is None:
            # all records received, no token - we have probably reached the end
            print("No further records, all done.", file=sys.stderr)
            break

    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        print("Waiting for 10 seconds before retrying...", file=sys.stderr)
        time.sleep(10)
