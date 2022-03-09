# Sampled stream data ingestion

The script `get_sampled_stream.py` is run as a systemd service.

See [this guide](https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267) on how to set up a systemd service.

The systemd unit file for this service looks like this:

[Unit]
Description=My test service
After=multi-user.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
ExecStart=/usr/local/anaconda3/bin/python /home/jlasser/twitter_sampled_stream_v2/get_sampled_stream_medea.py
RestartSec=3

[Install]
WantedBy=multi-user.target

Notes:
* Make sure the correct path to the python executable is supplied.
* Make sure the location of twarc is in the pythonpath.
* Make sure the python executable only uses absolute paths
* Systemd services run as root. I tried to get them working for a user but failed. Mainly because the service then wouldn't start at machine reboot.
* Files created by the python script run as a service are owned by root.
* Test if the systemd service is running: systemctl is-active <service name> >/dev/null 2>&1 && echo YES || echo NO
