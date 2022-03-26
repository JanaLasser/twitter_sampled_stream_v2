import sampled_stream_functions as ssf
import socket
import datetime
from os.path import join
import sys

cwd = sys.argv[1] 
server_settings = {}
with open(join(cwd, "server_settings.txt"), 'r') as f:
    for l in f:
        server_settings[l.split('=')[0]] = l.split('=')[1].strip('\n')
        
email_credentials_dst = server_settings["EMAIL_CREDENTIALS_DST"]
email_credentials_filename = server_settings["EMAIL_CREDENTIALS_FILENAME"]
        
data_src = server_settings["DATA_VAULT_DST"]
host = socket.gethostname()

yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
yesterday = "{}-{:02d}-{:02d}"\
    .format(yesterday.year, yesterday.month, yesterday.day)

with open(join(data_src, yesterday, f"{yesterday}_report.txt"), "r") as report_file:
    body = report_file.read()

ssf.notify(
    f"[NOTICE] daily report from {host}",
    body, 
    credential_src=email_credentials_dst,
    credential_fname=email_credentials_filename
)