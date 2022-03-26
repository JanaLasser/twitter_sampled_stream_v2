source server_settings.txt

DAY=$(date +%Y-%m-%d -d  "1 hour ago")
HOUR=$(date +%H -d  "1 hour ago")

for file in $data_storage_dst/$DAY/$HOUR/*.jsonl
do
    echo "[]" | $repository_dst/code/create_csv_head.jq > "${file%.jsonl}.csv"
    cat "$file" | $repository_dst/code/parse_tweets.jq >> "${file%.jsonl}.csv"
    rm "$file"
done

