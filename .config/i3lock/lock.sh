#!/usr/bin/env bash

# Suspend message display cleanly via systemd
# killall blueman-applet
systemctl --user stop blueman-applet

# Run the lock script in the foreground
# The script will pause here until the lock screen is dismissed
/home/abhi/.config/i3lock/i3lock.sh

# Resume message display after unlocking
# killall blueman-applet
# sleep 1
# systemctl --user start blueman-applet