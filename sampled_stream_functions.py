from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from os.path import join
import json

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

def get_twitter_API_credentials(name="jana", keydst="twitter_API_keys"):
    '''
    Returns the bearer tokens to access the Twitter v2 API for a list of users.
    '''
    credentials = {}
    with open(join(keydst, f"twitter_API_{name}.txt"), 'r') as f:
        for l in f:
            if l.startswith("bearer_token"):
                credentials[l.split('=')[0]] = l.split('=')[1].strip('\n')
    return credentials


def notify(subject, body, credential_src=os.getcwd()):
    '''
    Writes an email with the given subject and body from a mailserver specified
    in the email_credentials.txt file at the specified location. The email
    address to send the email to is also specified in the credentials file.
    '''
    email_credentials = {}
    with open(join(credential_src, "email_credentials.txt"), "r") as f:
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


def dump_tweets(tweets, t1, t2, dst):
    '''Save a list of tweets as binary line-separated json'''
    
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
        
    fname = f"sampled_stream_{datetime1}_to_{datetime2}.jsonl"

    with open(join(dst, daydirname, hourdirname, fname), 'wb') as f:
        for tweet in tweets:
            json_str = json.dumps(tweet) + "\n"
            json_bytes = json_str.encode('utf-8')
            f.write(json_bytes)      