import os
from os.path import join
import datetime
import sys
import osfclient
from osfclient.utils import norm_remote_path

storage = "osfstorage" # seems to be the name of the default OSF storage provider
project_ID = "dqx39" # get this from the URL of the project in the browser

## load the settings for the server we are running on ##
# cwd is passed via the command line, since when running as a service we can't
# get the current working directory via os.getcwd()
cwd = sys.argv[1] 
server_settings = {}
with open(join(cwd, "server_settings.txt"), 'r') as f:
    for l in f:
        server_settings[l.split('=')[0]] = l.split('=')[1].strip('\n')

# file I/O paths and folder names
src = server_settings["DATA_VAULT_DST"]
prev_hour = datetime.datetime.today() - datetime.timedelta(hours=1)
yearmonthday = "{}-{:02d}-{:02d}"\
    .format(prev_hour.year, prev_hour.month, prev_hour.day)
year = "{:04d}".format(prev_hour.year)
month = "{:02d}".format(prev_hour.month)
day = "{:02d}".format(prev_hour.day)
hour = "{:02d}".format(prev_hour.hour)
local_path = join(src, yearmonthday)
remote_path = join(year, month, day)

## set up the OSF client ##
# load the credentials
osf_credentials = {}
with open(
    join(server_settings["OSF_KEY_DST"],
         server_settings["OSF_KEY_FILENAME"]), "r") as credfile:
    for l in credfile:
        osf_credentials[l.split("=")[0]] = l.split("=")[1].strip("\n")     

# initialize the client
osf = osfclient.OSF(
    username=osf_credentials["username"],
    token=osf_credentials["token"]
)
# initialize the project (can also be a "component" of a larger project)
project = osf.project(project_ID)
store = project.storage(storage)

## upload tweet IDs and the daily report to the repository
fname_IDs = f"{yearmonthday}_{hour}_IDs.txt.xz"
fname_report = f"{yearmonthday}_report.txt"
for fname in [fname_IDs, fname_report]:
    if os.path.exists(join(local_path, fname)):
        with open(join(local_path, fname), 'rb') as fp:
            try:
                store.create_file(join(remote_path, fname), fp, force="f")
            except FileExistsError:
                print(f"not writing {fname} because file exists at OSF")
    else:
        print(f"not uploading {join(local_path, fname)} because file doesn't exist locally")
