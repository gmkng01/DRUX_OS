#!/bin/sh

case $1 in
up)
    pamixer --allow-boost -i 1
    send_notification
    ;;
down)
    pamixer --allow-boost -d 1
    send_notification
    ;;
mute)
    pamixer -t
    send_notification
    ;;
mice_mute)
    pamixer --default-source -t
    send_notification
    ;;
*)
    echo "Usage: $0 {up|down|mute|mice_mute}"
    exit 1
    ;;
esac