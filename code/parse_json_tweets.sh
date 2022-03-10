for file in data/2022-03-10/16/*
do
    echo "[]" | ./create_csv_head.jq > "${file%.json}.csv"
    cat "$file" | ./parse_tweets.jq >> "${file%.json}.csv"
    rm "$file"
done