#!/bin/bash

STATE_FILE="/tmp/nightlight_state"

if [ -f "$STATE_FILE" ]; then
    # Turn off night light
    redshift -x
    pkill redshift
    rm "$STATE_FILE"
else
    # Turn on night light
    redshift -O 4000
    touch "$STATE_FILE"
fi