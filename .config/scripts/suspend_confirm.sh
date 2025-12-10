#!/usr/bin/env bash

theme='/home/abhi/.config/rofi/theme'

yes='✓ Yes'
no='󰛉  No'

confirm_cmd() {
	rofi -theme-str 'window {location: center; anchor: center; fullscreen: false; width: 210px;}' \
		-theme-str 'mainbox {children: [ "message", "listview" ]; font: "NFS Font Regular 13";}' \
		-theme-str 'listview {columns: 2; lines: 1;}' \
		-theme-str 'element-text {horizontal-align: 0.5;}' \
		-theme-str 'textbox {horizontal-align: 0.5;}' \
		-dmenu \
		-p 'Confirmation' \
		-mesg 'Suspend  ?' \
		-theme ${theme}.rasi
}

confirm_exit() {
	echo -e "$yes\n$no" | confirm_cmd
}

run_rofi() {
	echo -e "$suspend" | rofi_cmd
}

run_cmd() {
    selected="$(confirm_exit)"
    if [[ "$selected" == "$yes" ]]; then
		systemctl suspend
		~/.config/i3lock/lock.sh
    else
        exit 0
    fi
}

chosen="$(run_rofi)"
case ${chosen} in
    $reboot)
        run_cmd --suspend
esac
# End of script
# This script prompts the user to confirm if they want to suspend the system.
# If the user confirms, it executes the suspend command and locks the screen.
# If the user declines, it simply exits without taking any action.
# The script uses rofi for the user interface and applies a custom theme.
# The confirmation dialog includes two options: "Yes" and "No".