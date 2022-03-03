#!/bin/bash

touch toggle
python get_sampled_stream.py > get_sampled_stream_out.txt 2>get_sampled_stream_err.txt
python notify.py
rm toggle