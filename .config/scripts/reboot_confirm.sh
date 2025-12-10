#!/usr/bin/env bash

# Current Theme
theme="$HOME/.config/rofi/theme.rasi"

yes='  Yes'
no='󰛉  No'

# Confirmation CMD
confirm_cmd() {
	rofi -theme-str 'window {location: center; anchor: center; fullscreen: false; width: 210px;}' \
		-theme-str 'mainbox {children: [ "message", "listview" ];}' \
		-theme-str 'listview {columns: 2; lines: 1;}' \
		-theme-str 'element-text {horizontal-align: 0.5;}' \
		-theme-str 'textbox {horizontal-align: 0.5;}' \
		-dmenu \
		-p 'Confirmation' \
		-mesg 'Reboot  ?' \
		-theme ${theme}
}

# Ask for confirmation
confirm_exit() {
	echo -e "$yes\n$no" | confirm_cmd
}

# Pass variables to rofi dmenu
run_rofi() {
	echo -e "$reboot" | rofi_cmd
}

run_cmd() {
    selected="$(confirm_exit)"
    if [[ "$selected" == "$yes" ]]; then
        systemctl reboot
    else
        exit 0
    fi
}

# Actions
chosen="$(run_rofi)"
case ${chosen} in
    $reboot)
        run_cmd --reboot
esac
# End of script
# This script prompts the user to confirm if they want to reboot the system.
# If the user confirms, it executes the reboot command.
# If the user declines, it simply exits without taking any action.
# The script uses rofi for the user interface and applies a custom theme.
# The confirmation dialog includes two options: "Yes" and "No".
# The script is designed to be run in a terminal or as part of a larger script that handles system operations.
# It is a simple and effective way to ensure that the user intentionally wants to reboot the system, preventing accidental reboots.
# The script is written in Bash and uses standard commands like `systemctl` for managing system services.
# The use of rofi allows for a visually appealing and user-friendly interface for the confirmation dialog.
# The script is customizable, allowing users to