#!/bin/bash
/home/jlasser/twitter_sampled_stream_v2/code/parse_json_tweets.sh
/usr/local/anaconda3/bin/python /home/jlasser/twitter_sampled_stream_v2/code/collect_data.py
/usr/local/anaconda3/bin/python /home/jlasser/twitter_sampled_stream_v2/code/collect_data.py
/usr/local/anaconda3/bin/python /home/jlasser/twitter_sampled_stream_v2/code/upload_IDs_to_OSF.py /home/jlasser/twitter_sampled_stream_v2/code/

