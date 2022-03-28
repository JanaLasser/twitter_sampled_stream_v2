import m3inference
import sys
from os.path import join
import pandas as pd
import numpy as np

fpath = sys.argv[1]
fname = sys.argv[2]
keyfile = sys.argv[3]
cachepath = sys.argv[4]

m3Twitter = m3inference.M3Twitter(cache_dir=cachepath)
m3Twitter.twitter_init_from_file(keyfile)

users = pd.read_csv(join(fpath, fname), dtype={"author_id":str})
user_ids = users["author_id"]
preds = pd.DataFrame({"author_id":user_ids})
preds['female_prob'] = np.nan
preds['age_<=18_prob'] = np.nan
preds['age_19-29_prob'] = np.nan
preds['age_30-39_prob'] = np.nan
preds['age_>=40_prob'] = np.nan
preds['org_prob'] = np.nan
preds = preds.set_index("author_id")

outputs = m3Twitter.infer_ids(user_ids, batch_size=100, num_workers=10)

for output in outputs:
    user_id = output['input']['id']
    pred = output['output']
    preds.loc[user_id, 'female_prob'] = pred['gender']['female']
    preds.loc[user_id, 'age_<=18_prob'] = pred['age']['<=18']
    preds.loc[user_id, 'age_19-29_prob'] = pred['age']['19-29']
    preds.loc[user_id, 'age_30-39_prob'] = pred['age']['30-39']
    preds.loc[user_id, 'age_>=40_prob'] = pred['age']['>=40']
    preds.loc[user_id, 'org_prob'] = pred['org']['is-org']
    
preds.to_csv(join(fpath, fname.split(".")[0] + "_preds.csv"))