#!/bin/bash

FILE=toggle
if [[ -f "$FILE" ]]; then
    echo "$FILE exist"
    exit
fi

./run_get_sampled_stream.sh