#!/bin/bash
cd /home/jlasser/twitter_sampled_stream_v2/code
source server_settings.txt

./parse_json_tweets.sh
$PYTHON_DST/python collect_data.py $REPOSITORY_DST/code/
$PYTHON_DST/python upload_IDs_to_OSF.py $REPOSITORY_DST/code/

