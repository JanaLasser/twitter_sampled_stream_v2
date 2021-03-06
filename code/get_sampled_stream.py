import os
from os.path import join
import sys
import json
import datetime
import socket
import pwd
import grp

## load the settings for the server we are running on ##
# cwd is passed via the command line, since when running as a service we can't
# get the current working directory via os.getcwd()
cwd = sys.argv[1] 
server_settings = {}
with open(join(cwd, "server_settings.txt"), 'r') as f:
    for l in f:
        server_settings[l.split('=')[0]] = l.split('=')[1].strip('\n')
server = server_settings["SERVER"]

# insert the library destination into the pythonpath and load third-party libs
sys.path.insert(0, server_settings["PYTHON_LIBRARY_DST"])
import pandas as pd
from twarc import Twarc2
from twarc.expansions import flatten

# custom functions for the stream scraper
import sampled_stream_functions as ssf

notifications = server_settings["NOTIFICATIONS"]
notifications = {"True":True, "False":False}[notifications]
if notifications:
    email_credentials_dst = server_settings["EMAIL_CREDENTIALS_DST"]
    email_credentials_filename = server_settings["EMAIL_CREDENTIALS_FILENAME"]

API_key_dst = server_settings["TWITTER_API_KEY_DST"]
API_key_filename = server_settings["TWITTER_API_KEY_FILENAME"]
data_storage_dst = server_settings[f"TMP_STORAGE_SERVER_{server}"]
username = server_settings["USERNAME"]
groupname = server_settings["GROUPNAME"]
uid = pwd.getpwnam(username).pw_uid
gid = grp.getgrnam(groupname).gr_gid
host = socket.gethostname()
credentials = ssf.get_twitter_API_credentials(
    filename=API_key_filename, 
    keydst=API_key_dst)
bearer_token = credentials["bearer_token"]
client = Twarc2(bearer_token=bearer_token)

dumptime = 60 # time [in seconds] at which the stream is dumped to disk

tweets = []
keys = ["max1", "max2", "max3", "max4", "max5", "max6",
        "alina", "anna", "emma", "hannah", "jana"]
keysrc = "/home/jlasser/utilities/twitter_API_v1_keys"
m3params = {
    "m3path":"/data/twitter_sampled_stream_v2_test/m3_classifications",
    "cachepath":"/data/twitter_sampled_stream_v2_test/m3_cache",
    "keyfile":None,
    "scriptpath":join(server_settings["REPOSITORY_DST"], "code")
}

m3classify = server_settings["M3CLASSIFY"]
m3classify = {"True":True, "False":False}[m3classify]

start = datetime.datetime.now()
header = f"[NOTICE] started sampled stream on {host}!"
if notifications:
    ssf.notify(
        header,
        str(start), 
        credential_src=email_credentials_dst,
        credential_fname=email_credentials_filename
    )
else:
    print(header)

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
                ssf.dump_tweets(tweets, start, now, data_storage_dst, uid, gid)
                
                if m3classify:
                    keyname = keys.pop()
                    keyfile = join(keysrc, f"m3_auth_v1_{keyname}.txt")
                    m3params["keyfile"] = keyfile
                    ssf.classify_users(start, now, data_storage_dst, m3params)
                    keys = [keyname] + keys
                    
                tweets = []
                start = datetime.datetime.now()
                
except Exception as e:
    header = f"[WARNING] sampled stream terminated on {host}!"
    if notifications:
        ssf.notify(
            header,
            str(e),
            credential_src=email_credentials_dst,
            credential_fname=email_credentials_filename
        )
    else:
        print(header)
        
        
