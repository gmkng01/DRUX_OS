#!/bin/sh

# 1. Set your wallpaper
~/.fehbg &

# 2. Disable screen blanking
xset s off -dpms

# 3. Tell systemd about your X11 session BEFORE Qtile starts
systemctl --user import-environment DISPLAY XAUTHORITY

# 4. Launch Qtile wrapped in a dbus session
exec dbus-run-session qtile start