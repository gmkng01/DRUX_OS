# !/usr/bin/env bash

# picom --no-fading-openclose &
# sleep 1

# ~/.config/qtile/trayer.py &

# nm-applet &
# blueman-applet &
# volctl &

# nitrogen --restore &

# # polkit (this is usually what people *actually* need)
# /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &

# ~/.config/scripts/battery_low.sh &

# Trayer 
# if pgrep -x "trayer" > /dev/null; then
#     # If running, kill trayer
#     killall trayer
# fi
# trayer --transparent true --width 5 --edge top --align right --alpha 0 --tint 0x2C3333 --margin 27 --distance 0 --distancefrom top &



# Power Managment
# xfce4-power-manager &

# emacs --daemon &






LOG="$HOME/.cache/qtile-autostart.log"
mkdir -p "$(dirname "$LOG")"
exec >>"$LOG" 2>&1

# echo "==== Qtile autostart: $(date) ===="

run() {
    if pgrep -x "$1" >/dev/null; then
        # echo "Already running: $1"
    else
        # echo "Starting: $*"
        "$@" &
    fi
}

# --- compositor ---
run picom --no-fading-openclose

# --- wallpaper ---
nitrogen --restore &

# --- polkit agent ---
run /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1

# --- START TRAY (CRITICAL) ---
if ! pgrep -f trayer.py >/dev/null; then
    # echo "Starting trayer..."
    ~/.config/qtile/trayer.py &
fi

# --- WAIT FOR TRAY TO EXIST ---
echo "Waiting for system tray..."
for i in {1..20}; do
    if xprop -root _NET_SYSTEM_TRAY_S0 >/dev/null 2>&1; then
        # echo "Tray detected"
        break
    fi
    sleep 0.3
done

# --- tray-dependent apps ---
run nm-applet
run blueman-applet
run volctl

# --- battery notifier ---
run ~/.config/scripts/battery_low.sh

# echo "Autostart complete"
