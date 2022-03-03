import json
from os import listdir
import os
import datetime
from os.path import join
import lzma

def load_json_tweets(fname, src):
    json_tweets = []
    with lzma.open(join(src, fname), 'rb') as f:
        for json_bytes in f.readlines():
            try:
                json_str = json_bytes.decode('utf-8')
                json_tweet = json.loads(json_str)   
                json_tweets.append(json_tweet)
            except json.JSONDecodeError:
                print(f"JSONDecodeError for file {fname}")
    #print(f"loaded {len(json_tweets)} tweets")
    return json_tweets


def dump_hour_tweets(tweets, t1, t2, dst):
    '''Save a list of tweets as xz compressed json'''
        
    fname = f"sampled_stream_{t1}_to_{t2}.xz"

    with lzma.open(join(dst, fname), 'wb') as f:
        for tweet in tweets:
            json_str = json.dumps(tweet) + "\n"
            json_bytes = json_str.encode('utf-8')
            f.write(json_bytes)     

            
dst = "data"

yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
hours = range(1, 25)

daydirname = "{}-{:02d}-{:02d}"\
        .format(yesterday.year, yesterday.month, yesterday.day)


for hour in hours:
    if os.path.exists(join(dst, daydirname, str(hour))):
        files = listdir(join(dst, daydirname, str(hour)))
        files.sort()
        start = files[0].split("_")
        start = "{}_{}".format(start[2], start[3])
        end = files[-1].split("_")
        end = "{}_{}".format(end[5], end[6].split(".")[0])
        
        json_tweets = []
        for f in files:
            json_tweets.extend(\
                    load_json_tweets(f, join(dst, daydirname, str(hour))))
            
        print(f"day {daydirname}, hour {hour}, total: {len(json_tweets)} tweets")
        
        dump_hour_tweets(json_tweets, start, end, join(dst, daydirname, str(hour)))
        
        for f in files:
            os.remove(join(dst, daydirname, str(hour), f))





