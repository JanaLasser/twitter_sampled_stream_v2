#!/bin/bash

echo "[]" | ./create_csv_head.jq > "${3}/${2%.jsonl}.csv"
cat "$1/$2" | ./parse_tweets.jq >> "${3}/${2%.jsonl}.csv"

python extract_users.py "${3}" "${2%.jsonl}.csv"
python classify_users.py "${3}" "${2%.jsonl}_users.csv" "${4}" "${5}"

rm "${3}/${2%.jsonl}.csv"
rm "${3}/${2%.jsonl}_users.csv"