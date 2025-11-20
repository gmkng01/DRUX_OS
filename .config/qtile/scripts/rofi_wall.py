#!/usr/bin/env python3

import os
import subprocess
import os
import re
from colorthief import ColorThief

home = os.path.expanduser('~')
NITROGEN_CFG_PATH = f"{home}/.config/nitrogen/bg-saved.cfg"
LOCK_SCRIPT_PATH = f"{home}/.config/i3lock/lock.sh"
LOGIN_IMAGE_DEST = "/usr/share/sddm/themes/Sugar-Candy/Backgrounds/background.jpg"

def show_option_selector():
    options = "Desktop\nLock\nLogin"
    result = subprocess.run(
        ['rofi', '-dmenu', '-p', 'Choose wallpaper type:','-theme', '~/.config/rofi/themes.rasi'],
        input=options,
        text=True,
        stdout=subprocess.PIPE
    )
    if result.returncode == 0:
        return result.stdout.strip().lower()
    return None

def select_image():
    try:
        result = subprocess.run([
            "zenity", "--file-selection", "--title=Choose an image",
            "--file-filter=*.png *.jpg *.jpeg *.bmp *.webp"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        print("Zenity not found.")
    return None

def show_message(title, message, is_error=False):
    icon = "--error" if is_error else "--info"
    subprocess.run(["zenity", icon, "--title", title, "--text", message])

def set_desktop_wallpaper(image_path):
    if not os.path.exists(NITROGEN_CFG_PATH):
        show_message("Error", "Nitrogen config not found.", True)
        return
    with open(NITROGEN_CFG_PATH, 'r') as f:
        lines = f.readlines()
    with open(NITROGEN_CFG_PATH, 'w') as f:
        for line in lines:
            if line.startswith("file="):
                f.write(f"file={image_path}\n")
            else:
                f.write(line)
    
    subprocess.run(["nitrogen", "--restore"])
    subprocess.run(
    'qtile cmd-obj -o cmd -f restart && source ./color_changer.sh && sleep 3 && ~/.config/qtile/trayer.py &',
    shell=True)
    subprocess.run('sleep 1',shell=True)
    subprocess.run('~/.config/qtile/trayer.py',shell=True)
    # show_message("Success", "Desktop wallpaper updated.")

def set_lock_screen(image_path):
    if not os.path.exists(LOCK_SCRIPT_PATH):
        show_message("Error", "Lock screen script not found.", True)
        return
    with open(LOCK_SCRIPT_PATH, 'r') as f:
        lines = f.readlines()
    with open(LOCK_SCRIPT_PATH, 'w') as f:
        for line in lines:
            if "--image=" in line:
                start = line.find("--image=")
                before = line[:start]
                f.write(f'{before}--image="{image_path}" \\\n')
            else:
                f.write(line)
    # show_message("Success", "Lock screen wallpaper updated.")

def set_login_screen(image_path):
    if not os.path.exists(image_path):
        show_message("Error", "Selected image does not exist.", True)
        return
    try:
        subprocess.run(["pkexec", "cp", image_path, LOGIN_IMAGE_DEST], check=True)
        # show_message("Success", "Login screen wallpaper updated.")
    except subprocess.CalledProcessError:
        show_message("Error", "Failed to copy image. You may need to install 'polkit' or run this as root.", True)

def main():
    target = show_option_selector()
    if not target:
        return
    image_path = select_image()
    if not image_path:
        return

    if target == "lock":        
        sh_file = "/home/abhi/.config/i3lock/lock.sh"
        ct = ColorThief(image_path)
        palette = ct.get_palette(color_count=2)
        fr  = f"#{palette[0][0]:02X}{palette[0][1]:02X}{palette[0][2]:02X}"
        fr2 = f"#{palette[1][0]:02X}{palette[1][1]:02X}{palette[1][2]:02X}"
        with open(sh_file, "r") as f:
            content = f.read()

        content = re.sub(r'^fr="#[0-9A-Fa-f]{6}"',  f'fr="{fr}"',  content, flags=re.MULTILINE)
        content = re.sub(r'^fr2="#[0-9A-Fa-f]{6}"', f'fr2="{fr2}"', content, flags=re.MULTILINE)

        with open(sh_file, "w") as f:
            f.write(content)
        # print("Updated:", fr, fr2)
        set_lock_screen(image_path)

    elif target == "desktop":
        set_desktop_wallpaper(image_path)    
    elif target == "login":
        set_login_screen(image_path)

if __name__ == "__main__":
    main()
