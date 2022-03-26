from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from os.path import join
import json
import pandas as pd
import subprocess


USER_FIELDS = [
    "created_at",
    #"description",
    #"entities",
    "id",
    "location",
    "name",
    #"pinned_tweet_id",
    #"profile_image_url",
    "protected",
    "public_metrics",
    #"url",
    "username",
    "verified",
    #"withheld",
]

TWEET_FIELDS = [
    #"attachments",
    "author_id",
    #"context_annotations",
    "conversation_id",
    "created_at",
    #"entities",
    #"geo",
    "id",
    #"in_reply_to_user_id",
    "lang",
    #"public_metrics",
    "text",
    #"possibly_sensitive",
    "referenced_tweets",
    #"reply_settings",
    "source",
    #"withheld",
]

EXPANSIONS = ["author_id"]

DTYPES = {
    "id": str, 
    "conversation_id":str,
    "author_id":str,
    #"created_at":str,
    #"retrieved_at":str, 
    "source":str,
    "lang":str,
    "text":str,
    "reference_type":str,
    "referenced_tweet_id":str,
    #"author.created_at":str,
    "author.location":str, 
    "author.name":str, 
    "author.username":str, 
    "author.verified":str, 
    "author.protected":str,
    "author.public_metrics.followers_count":float, 
    "author.public_metrics.following_count":float,
    "author.public_metrics.tweet_count":float,
    "author.public_metrics.listed_count":float}

AUTHOR_COLS = [
    "author_id", "lang", "author.created_at", "author.location",
    "author.name", "author.username", "author.verified",
    "author.protected", "author.public_metrics.followers_count",
    "author.public_metrics.following_count",
    "author.public_metrics.tweet_count",
    "author.public_metrics.listed_count"]


def get_twitter_API_credentials(filename="twitter_API_jana.txt", keydst="twitter_API_keys"):
    '''
    Returns the bearer tokens to access the Twitter v2 API for a list of users.
    '''
    credentials = {}
    with open(join(keydst, filename), 'r') as f:
        for l in f:
            if l.startswith("bearer_token"):
                credentials[l.split('=')[0]] = l.split('=')[1].strip('\n')
    return credentials


def notify(subject, body, credential_src=os.getcwd(), 
           credential_fname="email_credentials.txt"):
    '''
    Writes an email with the given subject and body from a mailserver specified
    in the email_credentials.txt file at the specified location. The email
    address to send the email to is also specified in the credentials file.
    '''
    email_credentials = {}
    with open(join(credential_src, credential_fname), "r") as f:
        for line in f.readlines():
            line = line.strip("\n")
            email_credentials[line.split("=")[0]] = line.split("=")[1]
            
    fromaddr = email_credentials["fromaddr"]
    toaddr = email_credentials["toaddr"]
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(
        email_credentials["server"],
        int(email_credentials["port"])
    )
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email_credentials["user"], email_credentials["password"])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)


def dump_tweets(tweets, t1, t2, dst, uid, gid):
    '''Save a list of tweets as binary line-separated json'''
    
    daydirname = "{}-{:02d}-{:02d}".format(t1.year, t1.month, t1.day)
    hourdirname = "{:02d}".format(t1.hour)

    if not os.path.exists(join(dst, daydirname)):
        os.mkdir(join(dst, daydirname))
        os.chown(join(dst, daydirname), uid, gid)
    
    
    if not os.path.exists(join(dst, daydirname, hourdirname)):
        os.mkdir(join(dst, daydirname, hourdirname))
        os.chown(join(dst, daydirname, hourdirname), uid, gid)
    
    datetime1 = "{}-{:02d}-{:02d}_{:02d}:{:02d}:{:02d}"\
        .format(t1.year, t1.month, t1.day, t1.hour, t1.minute, t1.second)
    datetime2 = "{}-{:02d}-{:02d}_{:02d}:{:02d}:{:02d}"\
        .format(t2.year, t2.month, t2.day, t2.hour, t2.minute, t2.second)
        
    fname = f"sampled_stream_{datetime1}_to_{datetime2}.jsonl"

    with open(join(dst, daydirname, hourdirname, fname), 'wb') as f:
        for tweet in tweets:
            json_str = json.dumps(tweet) + "\n"
            json_bytes = json_str.encode('utf-8')
            f.write(json_bytes)
            
    os.chown(join(dst, daydirname, hourdirname, fname), uid, gid)
    
    
def classify_users(t1, t2, dst, m3params):
    daydirname = "{}-{:02d}-{:02d}".format(t1.year, t1.month, t1.day)
    hourdirname = "{:02d}".format(t1.hour)
    datetime1 = "{}-{:02d}-{:02d}_{:02d}:{:02d}:{:02d}"\
        .format(t1.year, t1.month, t1.day, t1.hour, t1.minute, t1.second)
    datetime2 = "{}-{:02d}-{:02d}_{:02d}:{:02d}:{:02d}"\
        .format(t2.year, t2.month, t2.day, t2.hour, t2.minute, t2.second)
    fname = f"sampled_stream_{datetime1}_to_{datetime2}.jsonl"    
    
    scriptname = "run_m3_classification.sh"
    scriptpath = "/home/jana/Projects/CSS_sampled_stream/code/"
    fpath = join(dst, daydirname, hourdirname)
    m3path = m3params["m3path"]
    keyfile = m3params["keyfile"]
    cachepath = m3params["cachepath"]
    
    subprocess.Popen([f"{join(scriptpath, scriptname)} {fpath} {fname} {m3path} {keyfile} {cachepath}"], shell=True)
    
    
def get_hour_files(hour_dst):
    all_hour_files = os.listdir(hour_dst)
    hour_files = [f for f in all_hour_files if f.endswith(".csv")]
    
    if len(all_hour_files) != len(hour_files):
        print(f"too many files in {hour_dst}")
        
    hour_tweets = pd.DataFrame()
    for f in hour_files:
        tmp = pd.read_csv(
            join(hour_dst, f), 
            #error_bad_lines=False, 
            dtype=DTYPES, 
            parse_dates=["created_at", "retrieved_at", "author.created_at"]
        )
        hour_tweets = pd.concat([hour_tweets, tmp])
    hour_tweets = hour_tweets.reset_index(drop=True)
    return hour_tweets