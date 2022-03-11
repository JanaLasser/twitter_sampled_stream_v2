DAY="2022-03-11"
#HOUR="1"

for HOUR in 2 3 4 5 6 7 8 9 10 11 12 13 14 15
do
    for DIR in tmp1 tmp2
    do
        for file in /data/twitter_sampled_stream_v2/$DIR/$DAY/$HOUR/*.jsonl
        do
            echo "[]" | ./create_csv_head.jq > "${file%.jsonl}.csv"
            cat "$file" | ./parse_tweets.jq >> "${file%.jsonl}.csv"
            rm "$file"
        done
    done
done
