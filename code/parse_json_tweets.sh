#!/bin/bash
cd /home/jlasser/twitter_sampled_stream_v2/code
source server_settings.txt

DAY=$(date +%Y-%m-%d -d  "1 hour ago")
HOUR=$(date +%H -d  "1 hour ago")

for DIR in tmp1 tmp2
    do
    for file in $TMP_STORAGE_SERVER_1/$DIR/$DAY/$HOUR/*.jsonl
    do
        echo "[]" | ./create_csv_head.jq > "${file%.jsonl}.csv"
        cat "$file" | ./parse_tweets.jq >> "${file%.jsonl}.csv"
        rm "$file"
    done
done

