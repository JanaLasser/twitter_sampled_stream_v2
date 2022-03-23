import os
from os.path import join
import datetime
import pandas as pd
import numpy as np
import shutil
import sampled_stream_functions as ssf
import sys

cwd = sys.argv[1] 
server_settings = {}
with open(join(cwd, "server_settings.txt"), 'r') as f:
    for l in f:
        server_settings[l.split('=')[0]] = l.split('=')[1].strip('\n')
src = server_settings["data_vault_dst"]

prev_hour = datetime.datetime.today() - datetime.timedelta(hours=1)
day = "{}-{:02d}-{:02d}"\
    .format(prev_hour.year, prev_hour.month, prev_hour.day)
hour = prev_hour.hour

if not os.path.exists(join(src, day)):
    # create folder for the day if it doesn't exist yet
    os.mkdir(join(src, day))
    
    # write header in the report file for the day
    with open(join(src, day, f"{day}_report.txt"), "a") as report_file:
        report_file.write(f"hour\tserv 1\tserv 2\ttotal\tdiff\tdiff %\n")
        

# get the tweets for the given hour from both servers
hourdirname = "{:02d}".format(hour)
tmp1 = ssf.get_hour_files(join(src, "tmp1", day, hourdirname))
tmp2 = ssf.get_hour_files(join(src, "tmp2", day, hourdirname))

# Extract the tweet IDs from bot datasets and calculate the difference
# Note: the difference between the two data sets can occur because
# (1) one server went offline for a while
# (2) the servers are dumping tweets every minute and might include some
#     tweets from the previous hour in the dump
# (3) the sampled stream was backfilling and captured tweets from the
#     previous hour
ids1 = set(tmp1["id"])
ids2 = set(tmp2["id"])
diff = len(ids1.symmetric_difference(ids2))

# combine the tweets from the two servers into one dataset that has all tweets
hour_tweets = pd.concat([tmp1, tmp2[~tmp2["id"].isin(tmp1["id"])]])\
    .drop_duplicates(subset=["id"])
N = len(hour_tweets)

# write the stats of the current hour into the report
print(f"{hour}\t{len(ids1)}\t{len(ids2)}\t{N}\t{diff}\t{round(diff/N * 100, 2)}%")
with open(join(src, day, f"{day}_report.txt"), "a") as report_file:
    report_file.write(f"{hour}\t{len(ids1)}\t{len(ids2)}\t{N}\t{diff}\t{round(diff/N * 100, 2)}%\n")

# extract unique users, keep user stats from the most recent post in case there is 
# more than one tweet by the same user
hour_users = hour_tweets[ssf.AUTHOR_COLS + ["created_at"]]\
    .sort_values(by="created_at", ascending=False)\
    .drop_duplicates(subset=["author_id"])\
    .drop(columns=["created_at"])

# save tweet IDs, unique users and tweets
np.savetxt(join(src, day, "{}_{:02d}_IDs.txt.xz".format(day, hour)),
           hour_tweets["id"].values, fmt="%s")

hour_users.to_csv(join(src, day, "{}_{:02d}_users.csv.xz".format(day, hour)),
          compression="xz", index=False)

hour_tweets.to_csv(join(src, day, "{}_{:02d}_tweets.csv.xz".format(day, hour)),
          compression="xz", index=False)

# clean up
shutil.rmtree(join(src, "tmp1", day, hourdirname))
shutil.rmtree(join(src, "tmp2", day, hourdirname))