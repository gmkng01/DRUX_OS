#!/bin/sh

# case $1 in
# up)
#     pamixer --allow-boost -i 1
#     # send_notification
#     ;;
# down)
#     pamixer --allow-boost -d 1
#     # send_notification
#     ;;
# mute)
#     pamixer -t
#     # send_notification
#     ;;
# mice_mute)
#     pamixer --default-source -t
#     # send_notification
#     ;;
# *)
#     echo "Usage: $0 {up|down|mute|mice_mute}"
#     exit 1
#     ;;
# esac



case "$1" in
up)
    wpctl set-volume @DEFAULT_AUDIO_SINK@ 1%+
    ;;
down)
    wpctl set-volume @DEFAULT_AUDIO_SINK@ 1%-
    ;;
mute)
    wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
    ;;
mice_mute)
    wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle
    ;;
*)
    echo "Usage: $0 {up|down|mute|mice_mute}"
    exit 1
    ;;
esac
