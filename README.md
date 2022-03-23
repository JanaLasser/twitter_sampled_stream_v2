# Sampled stream data ingestion
Code collects the tweets delivered by the Twitter API v2 [sampled stream](https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/introduction) endpoint. The sampled stream endpoint delivers a roughly 1% random sample of publicly available Tweets in real-time. I tweet IDs of the collected tweets in a public [OSF repository](https://osf.io/dqx39/). To get tweets from tweet IDs, read up on how to [hydrate tweets](https://twarc-project.readthedocs.io/en/latest/twarc2_en_us/#hydrate).

## Data collection architecture
The connection to the sampled stream is set up in parallel at two separate servers (server 1 and server 2) to provide redundancy if one of the server flatlines for some reason. If you want to implement a similar setup, you will have to clone this repository and go through the setup instructions on both servers. One of the servers (server 1) is the "main" server that collects and post-processes all data, reports if things go wrong and uploads the tweet IDs to the OSF repository every hour.  

## Setup [documentation is work in progress]
### Server settings
The various scripts will look for a file named `server_settings.txt` in the `/code` directory of this repository. This file collects all information relevant to run the scripts at the given server and should contain the following line-separated information (below I give examples, you need to replace them with the correct values for your server):

library_dst=/home/jana/anaconda3/lib/python3.8/site-packages 
API_key_dst=/home/jana/Projects/utilities/twitter_API_keys
OSF_key_dst=/home/jana/Projects/utilities/OSF
data_storage_dst=/home/jana/Projects/CSS_sampled_stream/tmp
data_vault_dst=/home/jana/Projects/CSS_sampled_stream/data
username=jana
groupname=jana

* `library_dst` is the path to the packages installed for your local python executable.
* `API_key_dst` is the path to a directory that contains the access information for your academic twitter API access. 

### Connection to the sampled stream
Connection to the sampled stream endpoing from the Twitter API is handled in the script `get_sampled_stream.py`.
The script is run as a systemd service to ensure it starts again if it terminates for some reason or the server reboots. See [this guide](https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267) on how to set up a systemd service.

The systemd unit file for this service should look something like this:

[Unit]
Description=Twitter sampled stream data collection
After=multi-user.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
ExecStart=[PATH_TO_PYTHON_EXECUTABLE] [PATH_TO_REPOSITORY]/get_sampled_stream.py
RestartSec=3

[Install]
WantedBy=multi-user.target

Notes:
* Make sure the correct path to the python executable is supplied.
* Make sure the location of twarc is in the pythonpath, since `get_sampled_stream.py` needs twarc to run.
* Systemd services run as root. I tried to get them working for a user but failed. Mainly because the service then wouldn't start at machine reboot.
* Files created by the python script run as a service are owned by root. File ownership is changed to the supplied user later in the `collect_data.py` script.
* Test if the systemd service is running: `systemctl is-active <service name> >/dev/null 2>&1 && echo YES || echo NO`
    
### Redundant data collection
The script `send_data.sh` needs to be hooked up to a (user) cronjob that runs every hour shortly after the full hour:
`7 * * * * /home/<user>/twitter_sampled_stream_v2/code/send_data.sh > /home/<user>/twitter_sampled_stream_v2/code/send_data.log 2>&1`
    
Note: the file structure is like below, with one folder for every day, and individual data files for every hour of the given day. Note that the days and hours refer to the CET time zone, while the timestamps inside the data (`created_at`, `retrieved_at` and `author.created_at`) refer to UTZ.
`YYYY-mm-dd`
    `YYYY-mm-dd_hh_IDs.txt.xz`
    `YYYY-mm-dd_hh_users.csv.xz`
    `YYYY-mm-dd_hh_tweets.csv.xz`
    `...`
    
### Data post-processing
TODO

### Data upload to OSF
TODO

## Setup without redundant server
TODO

## Setup without email notifications
TODO
