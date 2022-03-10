#! /usr/local/anaconda3/bin/python
import sys
sys.path.insert(0, "/home/jlasser/.local/lib/python3.8/site-packages/")
API_key_dst = '/home/jlasser/utilities/twitter_API_keys'
data_storage_dst = "/data/twitter_sampled_stream_v2"

from twarc import Twarc2
import pandas as pd
from os.path import join
import json
import datetime
import os
import socket

import sampled_stream_functions as ssf

host = socket.gethostname()
ssf.notify(f"[NOTICE] started sampled stream on {host}!", str(start))

API_key_name = "david"
credentials = ssf.get_twitter_API_credentials(API_key_name, keydst=API_key_dst)
bearer_token = credentials[credname]
client = Twarc2(bearer_token=bearer_token)

dumptime = 60 # time [in seconds] at which the stream is dumped to disk

tweets = []
start = datetime.datetime.now()
try:
    while True:
        for tweet in client.sample(
                event=None, 
                record_keepalive=True, 
                expansions=",".join(ssf.EXPANSIONS), 
                tweet_fields=",".join(ssf.TWEET_FIELDS),
                user_fields=",".join(ssf.USER_FIELDS),
                media_fields=[],
                poll_fields=[],
                place_fields=[],
                backfill_minutes=5
        ):
            if tweet == 'keep-alive':
                print("staying alive ...")
            else:
                try:
                    tweet = flatten(tweet)[0]
                    if not "referenced_tweets" in tweet.keys():
                        tweet["referenced_tweets"] = [{'type': 'original',
                                                       'id': None}]
                    tweets.append(tweet)
                except Exception as e:
                    print(Exception)

            now = datetime.datetime.now()
            if (start - now).seconds % dumptime == 0: # dump tweets every minute
                print("dumping tweets")
                ssf.dump_tweets(tweets, start, now, data_storage_dst)
                tweets = []
                start = datetime.datetime.now()
                
except Exception as e:
    ssf.notify(f"[WARNING] sampled stream terminated on {host}!", str(e))
        
        
