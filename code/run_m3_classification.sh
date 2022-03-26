#!/bin/bash

# $1: path to json
# $2: daydirname
# $3: hourdirname
# $4: json filename
# $5: path to results dir
# $6: absolute path to twitter API v1 keyfile
# $7: path to m3 cache

JSONDIR="${1}/${2}/${3}"
M3DIR="${5}/${2}/${3}"

if [ ! -f $M3DIR ]
then
    mkdir -p $M3DIR
fi

echo "[]" | ./create_csv_head.jq > "${M3DIR}/${4%.jsonl}.csv"
cat "$JSONDIR/$4" | ./parse_tweets.jq >> "${M3DIR}/${4%.jsonl}.csv"

python extract_users.py "${M3DIR}" "${4%.jsonl}.csv"
python classify_users.py "${M3DIR}" "${4%.jsonl}_users.csv" "${6}" "${7}"

rm "${M3DIR}/${4%.jsonl}.csv"
rm "${M3DIR}/${4%.jsonl}_users.csv"