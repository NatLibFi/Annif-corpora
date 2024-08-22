
import gzip
import json
import os.path
import requests
import sys
import time


headers = {
    'User-Agent': 'Annif-Finna-collect'
}


def fetch_ts(record_id):
    url = f'https://api.finna.fi/api/v1/record?id={record_id}&field[]=rawData'
    field = 'first_indexed'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'records' in data and len(data['records']) > 0:
            raw_data = data['records'][0].get('rawData', {})
            return raw_data.get(field, None)
    return None


def read_existing_timestamps(ts_file_path):
    timestamps = {}
    if os.path.exists(ts_file_path):
        with gzip.open(ts_file_path, 'rt') as ts_file:
            for ind, line in enumerate(ts_file):
                ts_record = json.loads(line)
                timestamps.update(ts_record)
    return timestamps


def write_timestamp(ts_file, ts):
    ndjson_line = json.dumps(ts)
    ts_file.write(ndjson_line + "\n")


def process_gzipped_file(file_path, timestamps):
    req_count = 0
    with (
        gzip.open(file_path, 'rt', encoding='utf-8') as records_file,
        gzip.open(ts_file_path, 'at', encoding='utf-8') as ts_file
        ):
        for line_ind, line in enumerate(records_file):
            rec = json.loads(line)
            rec_id = rec.get('id')
            if rec_id and rec_id not in timestamps:
                ts_new = {rec_id: fetch_ts(rec_id)}
                timestamps.update(ts_new)
                write_timestamp(ts_file, ts_new)
                req_count += 1
                if req_count % 50 == 0:
                    print(f"Input line {line_ind}, request count {req_count}")
                    # break
                    time.sleep(2)
    return timestamps


if len(sys.argv) < 2:
    print("Give ndjson filename as an argument.")
    sys.exit(1)
file_path = sys.argv[1]


# insert_pos = file_path.rfind(".ndjson.gz")
# ts_file_path = file_path[:insert_pos] + "-first-indexed" + file_path[insert_pos:]
ts_file_path = "finna-with-koko-uris-first-indexed-timestamps.ndjson.gz"


timestamps = read_existing_timestamps(ts_file_path)

process_gzipped_file(file_path, timestamps)
