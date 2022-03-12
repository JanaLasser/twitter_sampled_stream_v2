#!/bin/bash
rsync --remove-source-files -avze ssh /data/twitter_sampled_stream_v2/ jlasser@medea:/data/twitter_sampled_stream_v2/tmp2/