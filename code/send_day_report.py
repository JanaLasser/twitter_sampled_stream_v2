import sampled_stream_functions as ssf
import socket
import datetime
from os.path import join


credential_src = "/home/jlasser/twitter_sampled_stream_v2/code"
data_src = "/data/twitter_sampled_stream_v2/"
host = socket.gethostname()

yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
yesterday = "{}-{:02d}-{:02d}"\
    .format(yesterday.year, yesterday.month, yesterday.day)

with open(join(data_src, yesterday, f"{yesterday}_report.txt"), "r") as report_file:
    body = report_file.read()

ssf.notify(
    f"[NOTICE] daily report from {host}",
    body, 
    credential_src=credential_src
)