# Sampled stream data ingestion
Code collects the tweets delivered by the Twitter API v2 [sampled stream](https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/introduction) endpoint. The sampled stream endpoint delivers a roughly 1% random sample of publicly available Tweets in real-time. I tweet IDs of the collected tweets in a public [OSF repository](https://osf.io/dqx39/). To get tweets from tweet IDs, read up on how to [hydrate tweets](https://twarc-project.readthedocs.io/en/latest/twarc2_en_us/#hydrate).

## Data collection architecture
### Redundancy
The connection to the sampled stream is set up in parallel at two separate servers (server 1 and server 2) to provide redundancy if one of the server flatlines for some reason. If you want to implement a similar setup, you will have to clone this repository and go through the setup instructions on both servers. One of the servers (server 1) is the "main" server that collects and post-processes all data, reports if things go wrong and uploads the tweet IDs to the OSF repository every hour. 

### Data post-processing
**Note:** Set the paths at the beginning of the `process_hour_tweets.sh` and `parse_json_tweets.sh` (`parse_json_tweets_nonredundant.sh` for the non-redundant setup) to the correct paths corresponding to your server.  

Raw JSON data is post-processed every hour on server 1, to distribute compute load throughout the day. All processing operations are collected in the script `process_hour_tweets.sh`, which calls `parse_json_tweets.sh`, `collect_data.py` and `upload_IDs_to_OSF.py`. 

* `parse_json_tweets.sh` parses the raw JSON payload and flattens it into comma separated files using the `jq` utility. This is rather efficient and I haven't found the need to parallelize the operation to run on more than one core. Files are saved as `.csv` and the original `.jsonl` file is deleted.
* `collect_data.py` reads all `.csv` files for the given hour from both servers (there should be one for every minute of the hour) and combines them into two data frames: one from server 1 and the other from server 2. These data frames are then compared based on the unique ID of every tweet and the difference is calculated. This difference alongside the number of tweets from each server and the total number of tweets is written to the report file for the given day. The data from both servers is merged, making sure that tweets that might not have been recorded by one server are supplied by the other server. From the merged data, three files are saved at `data_vault_dst` (specified in `server_settings.txt`) and the original `.csv` files from both servers deleted:
    * The tweet IDs are saved as an xz-compresses `.txt` file to be later uploaded to OSF.
    * The tweet text and other tweet meta information are saved as an xz-compressed `.csv` file. See `sampled_stream_functions.py` `TWEET_FIELDS` and `USER_FIELDS` for a list of fields that are stored.
    * A list of unique users and some user statistics (see `sampled_stream_functions.AUTHOR_COLS`) are saved as xz-compressed `.csv` file.
* `upload_IDs_to_OSF.py` uploads the list of tweet IDs of the given hour to a public OSF repository.

The file structure in `data_vault_dst` is like below, with one folder for every day, and individual data files for every hour of the given day. Note that the days and hours refer to the CET time zone, while the timestamps inside the data (`created_at`, `retrieved_at` and `author.created_at`) refer to UTZ, as returned by the Twitter API.  

```
    YYYY-mm-dd
        YYYY-mm-dd_hh_IDs.txt.xz
        YYYY-mm-dd_hh_users.csv.xz
        YYYY-mm-dd_hh_tweets.csv.xz
        ...
```

## Step-by-step setup
What follows is the description of the full setup with redundant data collection, email notifications and automatic upload to an OSF repository. I also include some scripts to set up the data collection in a non-redundant way using only a single server - this is untested though (see [Setup without redundant server](#setup-without-redundant-server) below). Similarly, you can simplify the setup by turning off email notifications ([Setup without email notifications](#setup-without-email-notifications)) and OSF upload ([Setup without OSF upload](#setup-without-osf-upload)).

1. Both servers: clone the code repository
2. Both servers: Adapt the settings in `server_settings.txt` accordingly (see [Server settings](#server-settings) below).
3. Both servers: Make sure all file paths and files specified in your `server_settings.txt` file exist. This especially applies to your credentials for the Twitter API, email client credentials (if email notifications are turned on) and OSF credentials (if you also intend to upload things to OSF).
4. On server 1: Adapt the first line in `process_hour_tweets.sh` to match the location of your repository.
5. On server 1: Adapt the first line in `parse_json_tweets.sh` to match the location of your repository (do this in `parse_json_tweets_nonredundant.sh` if you are running the non-redundant setup as described below.
6. On server 2: Adapt the script `send_data.sh` to your setup by inserting the path to the repository on the server in the first line and adapting the ssh connection information to server 1 accordingly.
7. On server 2: Set up the cronjob for the `send_data.sh` script (see [Redundant data collection](#redundant-data-collection)).
8. On both servers: set up and start the data collection system service (see [Data ingestion from the sampled stream as a service](#data-ingestion-from-the-sampled-stream-as-a-service) below.)
9. On server 1: Set up the cronjob for email notifications (see [Email notifications](#email-notifications)).
10. On server 1: change the variables `storage` and `project_ID` in the script `upload_IDs_to_OSF.py` to the correct values for your OSF project.

You should thoroughly test your setup, since it can break in many ways. You can find the output of `stdout` and `stderr` of the scripts `process_hour_tweets.sh` (on server 1) in the file `process_hour_tweets.log` that is automatically created in the folder `/code` of this repository. Similarly, on server 2 you can find information about the workings of the `send_data.sh` script in `send_data.log`.

### Setup without redundant server [untested]
* Replace `parse_json_tweets.py` with `parse_json_tweets_nonredundant.py` in the script `process_hour_tweets.sh`. 
* Replace `collect_data.py` with `collect_data_nonredundant.py` in the script `process_hour_tweets.sh`. 
* Ignore all setup instructions for server 2.

### Setup without email notifications
* Set `notifications=False` in the `server_settings.txt` file. 
* Do not set up the cronjob for the `send_day_report.py` script.

### Setup without OSF upload
Remove the last line from the script `process_hour_tweets.sh`

## Server settings
The various scripts will look for a file named `server_settings.txt` in the `/code` directory of this repository. This file collects all information relevant to run the scripts at the given server and should contain the following line-separated information. See also the [example settings](https://github.com/JanaLasser/twitter_sampled_stream_v2/blob/main/code/server_settings.txt) uploaded in this repo.

* `SERVER`: should be set to "1" or "2" and tells various scripts which paths to use.
* `PYTHON_DST`: path to your system's python executable.
* `PYTHON_LIBRARY_DST`: path to the packages installed for your local python executable.
* `TWITTER_API_KEY_DST`: path to a directory that contains the access information for your academic twitter API access. 
* `TWITTER_API_KEY_FILENAME`: name of the file in which the API key is stored.
* `NOTIFICATIONS`: should be set to "True" or "False". Turns email notifications on or off.
* `M3ClASSIFY`: this is a flag for a feature that is in development. Feel free to ignore it.
* `EMAIL_CREDENTIALS_DST`: path to a directory that contains the credentials for your email server (only necessary if `NOTIFICATIONS=TRUE`).
* `EMAIL_CREDENTIALS_FILENAME`: name of the file in which the email server credentials are stored (only necessary if `NOTIFICATIONS=TRUE`).
* `TMP_STORAGE_SERVER_1`: path to the folder in which the data from the twitter API collected on server 1 is temporarily stored. Note: `get_sampled_stream.py` will check which `SERVER` it is running on and will choose the path accordingly.
* `TMP_STORAGE_SERVER_2`: path to the folder in which the data from the twitter API collected on server 2 is temporarily stored. Note: for server 1, this should be set to the folder to which the files from server 2 are copied, since `collect_data.py`, which is run on server 1 will look for files there.
* `REPOSITORY_DST`: path to this repository.
* `USERNAME`: ownership of files will be changed from root to the provided username.
* `GROUPNAME`: ownership of files will be changed from root to the provided groupname.
* `OSF_KEY_DST`: path to a directory that contains the access information for OSF (not necessary for setup without OSF upload, only necessary on server 1)
* `OSF_KEY_FILENAME`: name of the file in which the OSF access credentials are stored (not necessary for setup without OSF upload, only necessary on server 1)
* `DATA_VAULT_DST`: path to the folder in which the post-processed data will be stored (only necessary on server 1).

## Data ingestion from the sampled stream as a service
Connection to the sampled stream endpoint from the Twitter API is handled in the script `get_sampled_stream.py`.
The script is intended to be run as a systemd service to ensure it starts again if it terminates for some reason or the server reboots. Make sure to set this up on **both servers** in the redundant setup. See [this guide](https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267) on how to set up a systemd service.

The systemd unit file (I called it `get_sampled_stream.service`) in `etc/systemd/sysem` for this service should look something like this:

```
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
```

Notes:
* Make sure the correct path to the python executable is supplied in the `ExecStart` variable.
* Make sure the location of twarc is in the system's pythonpath, since `get_sampled_stream.py` needs twarc to run.
* Systemd services run as root. I tried to get them working for a user but failed. Mainly because the service then wouldn't start at machine reboot.
* Files created by the python script run as a service are owned by root. File ownership is changed to the user and group supplied in `server_settings.txt` under `USERNAME` and `GROUPNAME` later in the `collect_data.py` script.
* Test if the systemd service is running with

`systemctl is-active <service name> >/dev/null 2>&1 && echo YES || echo NO`

If `get_sampled_stream.py` is working correctly, it will create one folder for every day at `DATA_STORAGE_DST`, specified in the `server_settings.txt` file. Within that folder, an subfolder will be created for every hour of the day. In that subfolder, the raw JSON payload from the Twitter API will be saved every minute as uncompressed line-separated `.jsonl` file.

## Email notifications
If `get_sampled_stream.py` exits its main execution loop, something has gone wrong. I therefore set up a functionality that sends me an email if this happens. For this to work, you need to supply the credentials for a mailserver in the `server_settings.txt` file. I also provide the script `send_day_report.py`, which sends the data ingestion report of the day that is created by `collect_data.py` by email every day via a cronjob:  

`0 2 * * * <path_to_python_executable>/python <path_to_repository>/code/send_day_report.py`
    
## Redundant data collection
**Note:** For this to work you will need to be able to connect to server 2 from server 1 to copy data, if possible via ssh but scp will also work but require adapting the script `send_data.sh`.  

The script `send_data.sh` is intended to run **only on server 2**. It sends the raw JSON data over to server 1 every hour using `rsync` and deletes the data on server 2. Make sure to adapt this script with your ssh credentials to access server 1 from server 2 and the correct file path on server 1.

The script needs to be hooked up to a (user) cronjob that runs every hour shortly after the full hour to ensure that the last writing operation for the hour has been completed. An entry in the crontab that also pipes stdout and sterr to the file `send_data.log` looks like this (make sure to adapt the paths to your server's setup):  

`7 * * * * <path_to_repository>/code/send_data.sh > <path_to_repository>/code/send_data.log 2>&1`
    


