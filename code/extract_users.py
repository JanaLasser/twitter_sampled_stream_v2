from os.path import join
import pandas as pd
import numpy as np
import sys
import sampled_stream_functions as ssf

fpath = sys.argv[1]
fname = sys.argv[2]

wanted_languages = ["en", "es", "ar", "pt", "fr",
                    "it", "de", "ru", "pl", "nl"]

tweets = pd.read_csv(join(fpath, fname), lineterminator="\n",
                         dtype={"id":str, "author_id":str})
tweets = tweets[tweets["lang"].isin(wanted_languages)]

users = tweets[ssf.AUTHOR_COLS + ["created_at"]]\
    .sort_values(by="created_at", ascending=False)\
    .drop_duplicates(subset=["author_id"])\
    .drop(columns=["created_at"])

users.to_csv(join(fpath, fname.split(".")[0] + "_users.csv"), index=False)