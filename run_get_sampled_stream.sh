#!/bin/bash

touch toggle
python3 get_sampled_stream.py > get_sampled_stream_out.txt 2>get_sampled_stream_err.txt
python3 notify.py
rm toggle