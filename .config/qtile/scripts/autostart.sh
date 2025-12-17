#!/usr/bin/env bash

picom --no-fading-openclose &
sleep 1

nm-applet &
blueman-applet &
volctl &

nitrogen --restore &

# polkit (this is usually what people *actually* need)
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &

~/.config/scripts/battery_low.sh &

# Trayer 
# if pgrep -x "trayer" > /dev/null; then
#     # If running, kill trayer
#     killall trayer
# fi
# trayer --transparent true --width 5 --edge top --align right --alpha 0 --tint 0x2C3333 --margin 27 --distance 0 --distancefrom top &



# Power Managment
# xfce4-power-manager &

# emacs --daemon &
