#!/bin/bash
source server_settings.txt
rsync --remove-source-files -avze ssh $TMP_STORAGE_SERVER_2 jlasser@medea:/data/twitter_sampled_stream_v2/tmp2/
