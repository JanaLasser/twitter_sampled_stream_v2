#! /usr/bin/python3


import sys
sys.path.insert(0, "/home/jana/.local/lib/python3.9/site-packages/")


from twarc import Twarc2
import pandas as pd
from os.path import join
import json
import datetime
import lzma
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import socket


sys.path.append('/home/jana/utilities/twitter_functions')
import twitter_functions as tf

keydst = '/home/jana/utilities/twitter_API_keys'
credname = "david"
credentials = tf.get_twitter_API_credentials([credname], keydst=keydst)
bearer_token = credentials[credname]
client = Twarc2(bearer_token=bearer_token)

def notify(subject, body):
    fromaddr = "crawler@janalasser.at"
    toaddr = "jana.lasser@tugraz.at"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    email_credentials = {}
    with open("/home/jana/twitter_sampled_stream_v2/email_credentials.txt", "r") as f:
        for line in f.readlines():
            line = line.strip("\n")
            email_credentials[line.split("=")[0]] = line.split("=")[1]

    server = smtplib.SMTP(email_credentials["server"], int(email_credentials["port"]))
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email_credentials["user"], email_credentials["password"])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)


def dump_tweets(tweets, t1, t2, dst):
    '''Save a list of tweets as xz compressed json'''
    
    daydirname = "{}-{:02d}-{:02d}".format(t1.year, t1.month, t1.day)
    hourdirname = str(t1.hour)

    if not os.path.exists(join(dst, daydirname)):
        os.mkdir(join(dst, daydirname))
    
    
    if not os.path.exists(join(dst, daydirname, hourdirname)):
        os.mkdir(join(dst, daydirname, hourdirname))
    
    datetime1 = "{}-{:02d}-{:02d}_{:02d}:{:02d}:{:02d}"\
        .format(t1.year, t1.month, t1.day, t1.hour, t1.minute, t1.second)
    datetime2 = "{}-{:02d}-{:02d}_{:02d}:{:02d}:{:02d}"\
        .format(t2.year, t2.month, t2.day, t2.hour, t2.minute, t2.second)
        
    fname = f"sampled_stream_{datetime1}_to_{datetime2}.xz"

    with lzma.open(join(dst, daydirname, hourdirname, fname), 'wb') as f:
        for tweet in tweets:
            json_str = json.dumps(tweet) + "\n"
            json_bytes = json_str.encode('utf-8')
            f.write(json_bytes)   
            


start = datetime.datetime.now()
tweets = []

host = socket.gethostname()
notify(f"[NOTICE] started sampled stream on {host}!", str(start))

dst = "/data/twitter_sampled_stream_v2"
dumptime = 60 # time [in seconds] at which the stream is dumped to disk


try:
    while True:
        for tweet in client.sample(
                event=None, 
                record_keepalive=True, 
                expansions=[], 
                tweet_fields=None,
                user_fields=[],
                media_fields=[],
                poll_fields=[],
                place_fields=[],
                backfill_minutes=5
        ):
            if tweet == 'keep-alive':
                print("staying alive ...")
            else:
                try:
                    data = tweet["data"]
                    data["retrieved_at"]= tweet["__twarc"]["retrieved_at"]
                    tweets.append(data)
                except Exception as e:
                    print(Exception)

            now = datetime.datetime.now()
            if (start - now).seconds % dumptime == 0: # dump tweets every minute
                print("dumping tweets")
                dump_tweets(tweets, start, now, dst)
                tweets = []
                start = datetime.datetime.now()
                
except Exception as e:
    notify(f"[WARNING] sampled stream terminated on {host}!", str(e))
        
        
