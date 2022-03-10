#! /usr/local/anaconda3/bin/python
server_settings = {}
with open(f"server_settings.txt", 'r') as f:
    for l in f:
        server_settings[l.split('=')[0]] = l.split('=')[1].strip('\n')

import sys
sys.path.insert(0, server_settings["library_dst"])
from twarc import Twarc2
from twarc.expansions import flatten
import pandas as pd
from os.path import join
import json
import datetime
import os
import socket

import sampled_stream_functions as ssf

API_key_dst = server_settings["API_key_dst"]
data_storage_dst = server_settings["data_storage_dst"]
host = socket.gethostname()
API_key_name = "david"
credentials = ssf.get_twitter_API_credentials(API_key_name, keydst=API_key_dst)
bearer_token = credentials["bearer_token"]
client = Twarc2(bearer_token=bearer_token)

dumptime = 60 # time [in seconds] at which the stream is dumped to disk

tweets = []
start = datetime.datetime.now()
ssf.notify(f"[NOTICE] started sampled stream on {host}!", str(start))
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
                    print(e)

            now = datetime.datetime.now()
            if (start - now).seconds % dumptime == 0: # dump tweets every minute
                print("dumping tweets")
                ssf.dump_tweets(tweets, start, now, data_storage_dst)
                tweets = []
                start = datetime.datetime.now()
                
except Exception as e:
    ssf.notify(f"[WARNING] sampled stream terminated on {host}!", str(e))
        
        
