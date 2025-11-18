# import os
# import shutil
# import subprocess
# import tkinter as tk
# from tkinter import filedialog, messagebox
# home = os.path.expanduser('~')
# # Constants
# NITROGEN_CFG_PATH = f"{home}/.config/nitrogen/bg-saved.cfg"
# LOCK_SCRIPT_PATH = f"{home}/.config/i3lock/lock.sh"
# LOGIN_IMAGE_DEST = "/usr/share/pixmaps/background.png"

# def select_image():
#     return filedialog.askopenfilename(
#         title="Choose an image",
#         filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")]
#     )

# def set_desktop_wallpaper(image_path):
#     if not os.path.exists(NITROGEN_CFG_PATH):
#         messagebox.showerror("Error", "Nitrogen config not found.")
#         return
#     with open(NITROGEN_CFG_PATH, 'r') as f:
#         lines = f.readlines()
#     with open(NITROGEN_CFG_PATH, 'w') as f:
#         for line in lines:
#             if line.startswith("file="):
#                 f.write(f"file={image_path}\n")
#             else:
#                 f.write(line)
#     messagebox.showinfo("Success", "Desktop wallpaper updated.")

# def set_lock_screen(image_path):
#     if not os.path.exists(LOCK_SCRIPT_PATH):
#         messagebox.showerror("Error", "Lock screen script not found.")
#         return
#     with open(LOCK_SCRIPT_PATH, 'r') as f:
#         lines = f.readlines()
#     with open(LOCK_SCRIPT_PATH, 'w') as f:
#         for line in lines:
#             if "--image=" in line:
#                 start = line.find("--image=")
#                 before = line[:start]
#                 f.write(f'{before}--image="{image_path}" \\\n')
#             else:
#                 f.write(line)
#     messagebox.showinfo("Success", "Lock screen wallpaper updated.")

# def set_login_screen(image_path):
#     if not os.path.exists(image_path):
#         messagebox.showerror("Error", "Selected image does not exist.")
#         return
#     try:
#         subprocess.run(["pkexec", "cp", image_path, LOGIN_IMAGE_DEST], check=True)
#         messagebox.showinfo("Success", "Login screen wallpaper updated.")
#     except subprocess.CalledProcessError:
#         messagebox.showerror("Error", "Failed to copy image.\nYou may need to install 'polkit' or run this as root.")

# def handle_click(target):
#     image_path = select_image()
#     if not image_path:
#         return
#     if target == "desktop":
#         set_desktop_wallpaper(image_path)
#     elif target == "lock":
#         set_lock_screen(image_path)
#     elif target == "login":
#         set_login_screen(image_path)

# # GUI Setup
# root = tk.Tk()
# root.title("Wallpaper Changer")
# root.geometry("350x200")
# root.resizable(False, False)

# label = tk.Label(root, text="Select which wallpaper to change:", font=("Helvetica", 12))
# label.pack(pady=10)

# tk.Button(root, text="Desktop Wallpaper", width=25, command=lambda: handle_click("desktop")).pack(pady=5)
# tk.Button(root, text="Lock Screen Wallpaper", width=25, command=lambda: handle_click("lock")).pack(pady=5)
# tk.Button(root, text="Login Screen Wallpaper", width=25, command=lambda: handle_click("login")).pack(pady=5)

# root.mainloop()




#####****zenity version****#####

# import os
# import subprocess
# import tkinter as tk
# from tkinter import messagebox

# home = os.path.expanduser('~')

# # Constants
# NITROGEN_CFG_PATH = f"{home}/.config/nitrogen/bg-saved.cfg"
# LOCK_SCRIPT_PATH = f"{home}/.config/i3lock/lock.sh"
# LOGIN_IMAGE_DEST = "/usr/share/pixmaps/background.png"

# def select_image():
#     try:
#         result = subprocess.run([
#             "zenity", "--file-selection", "--title=Choose an image",
#             "--file-filter=*.png *.jpg *.jpeg *.bmp *.webp"
#         ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         if result.returncode == 0:
#             return result.stdout.strip()
#     except FileNotFoundError:
#         messagebox.showerror("Error", "Zenity is not installed.\nInstall it using: sudo pacman -S zenity")
#     return None

# def set_desktop_wallpaper(image_path):
#     if not os.path.exists(NITROGEN_CFG_PATH):
#         messagebox.showerror("Error", "Nitrogen config not found.")
#         return
#     with open(NITROGEN_CFG_PATH, 'r') as f:
#         lines = f.readlines()
#     with open(NITROGEN_CFG_PATH, 'w') as f:
#         for line in lines:
#             if line.startswith("file="):
#                 f.write(f"file={image_path}\n")
#             else:
#                 f.write(line)
#     messagebox.showinfo("Success", "Desktop wallpaper updated.")

# def set_lock_screen(image_path):
#     if not os.path.exists(LOCK_SCRIPT_PATH):
#         messagebox.showerror("Error", "Lock screen script not found.")
#         return
#     with open(LOCK_SCRIPT_PATH, 'r') as f:
#         lines = f.readlines()
#     with open(LOCK_SCRIPT_PATH, 'w') as f:
#         for line in lines:
#             if "--image=" in line:
#                 start = line.find("--image=")
#                 before = line[:start]
#                 f.write(f'{before}--image="{image_path}" \\\n')
#             else:
#                 f.write(line)
#     messagebox.showinfo("Success", "Lock screen wallpaper updated.")

# def set_login_screen(image_path):
#     if not os.path.exists(image_path):
#         messagebox.showerror("Error", "Selected image does not exist.")
#         return
#     try:
#         subprocess.run(["pkexec", "cp", image_path, LOGIN_IMAGE_DEST], check=True)
#         messagebox.showinfo("Success", "Login screen wallpaper updated.")
#     except subprocess.CalledProcessError:
#         messagebox.showerror("Error", "Failed to copy image.\nYou may need to install 'polkit' or run this as root.")

# def handle_click(target):
#     image_path = select_image()
#     if not image_path:
#         return
#     if target == "desktop":
#         set_desktop_wallpaper(image_path)
#     elif target == "lock":
#         set_lock_screen(image_path)
#     elif target == "login":
#         set_login_screen(image_path)

# # GUI Setup
# root = tk.Tk()
# root.title("Wallpaper Changer")
# root.geometry("350x200")
# root.resizable(False, False)

# label = tk.Label(root, text="Select which wallpaper to change:", font=("Helvetica", 12))
# label.pack(pady=10)

# tk.Button(root, text="Desktop Wallpaper", width=25, command=lambda: handle_click("desktop")).pack(pady=5)
# tk.Button(root, text="Lock Screen Wallpaper", width=25, command=lambda: handle_click("lock")).pack(pady=5)
# tk.Button(root, text="Login Screen Wallpaper", width=25, command=lambda: handle_click("login")).pack(pady=5)

# root.mainloop()

import os
import subprocess
import sys

home = os.path.expanduser('~')
NITROGEN_CFG_PATH = f"{home}/.config/nitrogen/bg-saved.cfg"
LOCK_SCRIPT_PATH = f"{home}/.config/i3lock/lock.sh"
LOGIN_IMAGE_DEST = "/usr/share/pixmaps/background.png"

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
    show_message("Success", "Desktop wallpaper updated.")

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
    show_message("Success", "Lock screen wallpaper updated.")

def set_login_screen(image_path):
    if not os.path.exists(image_path):
        show_message("Error", "Selected image does not exist.", True)
        return
    try:
        subprocess.run(["pkexec", "cp", image_path, LOGIN_IMAGE_DEST], check=True)
        show_message("Success", "Login screen wallpaper updated.")
    except subprocess.CalledProcessError:
        show_message("Error", "Failed to copy image. You may need to install 'polkit' or run this as root.", True)

def main():
    target = show_option_selector()
    if not target:
        return
    image_path = select_image()
    if not image_path:
        return

    if target == "desktop":
        set_desktop_wallpaper(image_path)
    elif target == "lock":
        set_lock_screen(image_path)
    elif target == "login":
        set_login_screen(image_path)

if __name__ == "__main__":
    main()
