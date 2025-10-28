#!/bin/sh

case $1 in

full)
    hyprshot -m active -m output -f SS_$(date +'%d-%m-%y_%H:%M').png -o ~/Pictures/Screenshots/
    send_notification
    ;;

window)
    hyprshot -m window -f SS_$(date +'%d-%m-%y_%H:%M').png -o ~/Pictures/Screenshots/
    send_notification
    ;;

region_save)
    hyprshot -m region -f SS_$(date +'%d-%m-%y_%H:%M').png -o ~/Pictures/Screenshots/
    send_notification
    ;;

region_clipboard_only)
    hyprshot -m region --clipboard -f SS_$(date +'%d-%m-%y_%H:%M').png
    send_notification
    ;;

*)
    echo "Usage: $0 {full|window|region_save|region_clipboard_only}"
    exit 1
    ;;

esac