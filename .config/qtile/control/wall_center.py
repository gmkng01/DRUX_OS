#!/usr/bin/env python3
import sys
import os
import re
import shutil
import subprocess
import tempfile
import time
import hashlib
from pathlib import Path
from typing import List

# Essential for Qtile config interaction
CONFIG_PATH = Path.home() / ".config/qtile"
sys.path.append(str(CONFIG_PATH))

try:
    import func_var
    import themes.Color_picker as cp
except ImportError:
    print("Warning: Qtile config modules not found. Check your paths.")

from PyQt6 import QtCore, QtGui, QtWidgets

# Try to import ColorThief for dynamic lockscreen colors
try:
    from colorthief import ColorThief
except ImportError:
    ColorThief = None

# ------------------------ Config ------------------------
HOME = Path.home()
DEFAULT_WALL_DIR = HOME / "Pictures" / "walls"
# feh = HOME / ".config" / "nitrogen" / "bg-saved.cfg"
feh = HOME / ".fehbg"
LOCK_SCRIPT_PATH = HOME / ".config" / "i3lock" / "lock.sh"
LOGIN_IMAGE_DEST = Path("/usr/share/pixmaps/background.jpeg")
QTILE_FUNC_VAR = CONFIG_PATH / "func_var.py"
COLOR_CHANGER_SH = CONFIG_PATH / "color_changer.sh"
THUMB_SIZE = 160
BATCH_SIZE = 15
THUMB_CACHE_DIR_NAME = ".wall_thumbs"

# UI Styling
FONT_FAMILY = "JetBrainsMono Nerd Font"
FONT_SIZE = 11

# Extract colors from func_var safely
try:
    co = func_var.co
    bk, fr, bk2, fr2, gr = co['bk'], co['fr'], co['bk2'], co['fr2'], co['gr']
except:
    bk, fr, bk2, fr2, gr = "#1a1b26", "#a9b1d6", "#24283b", "#7aa2f7", "#414868"

DARK_STYLESHEET = f"""
QWidget {{ background-color: {bk}; color: {fr}; font-family: "{FONT_FAMILY}"; font-size: {FONT_SIZE}pt; }}
QListWidget {{ background-color: {bk}; border: 1px solid {bk2}; outline: none; }}
QListWidget::item:selected {{ background-color: {fr2}; color: white; border-radius: 4px; }}
QPushButton {{ background-color: {bk2}; border: 1px solid {gr}; padding: 8px; border-radius: 4px; }}
QPushButton:hover {{ background-color: {fr2}; color: white; }}
QLineEdit, QComboBox {{ background-color: {bk2}; border: 1px solid {gr}; padding: 4px; color: {fr}; }}
QGroupBox {{ border: 1px solid {gr}; margin-top: 1.5ex; font-weight: bold; }}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; }}
"""

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

# ------------------------ Utilities ------------------------

def get_thumb_cache_path(image_path: Path, cache_dir: Path) -> Path:
    hash_name = hashlib.md5(str(image_path).encode()).hexdigest()
    return cache_dir / f"{hash_name}.png"

def run_shell(cmd):
    """Non-blocking shell execution"""
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Shell Error: {e}")

# ------------------------ GUI ------------------------

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qtile Style Center")
        self.resize(1100, 750)
        self.image_path = None
        self._files_to_load = []
        self._load_index = 0
        
        self.init_ui()
        self.on_load_directory()

    def init_ui(self):
        self.setStyleSheet(DARK_STYLESHEET)
        main_layout = QtWidgets.QHBoxLayout(self)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        # --- Left Side ---
        left_container = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_container)

        self.preview_label = QtWidgets.QLabel("Select a wallpaper")
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(f"background-color: {bk2}; border-radius: 10px;")
        self.preview_label.setMinimumHeight(300)

        self.thumb_list = QtWidgets.QListWidget()
        self.thumb_list.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.thumb_list.setIconSize(QtCore.QSize(THUMB_SIZE, THUMB_SIZE))
        self.thumb_list.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.thumb_list.setSpacing(10)
        self.thumb_list.currentItemChanged.connect(self.on_selection_changed)

        self.dir_edit = QtWidgets.QLineEdit(str(DEFAULT_WALL_DIR))
        self.dir_edit.returnPressed.connect(self.on_load_directory)

        left_layout.addWidget(self.preview_label, stretch=3)
        left_layout.addWidget(self.thumb_list, stretch=2)
        left_layout.addWidget(self.dir_edit)

        # --- Right Side ---
        right_container = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_container)

        # Themes
        right_layout.addWidget(QtWidgets.QLabel("Available Themes"))
        self.theme_list = QtWidgets.QListWidget()
        themes = ["Darks", "Black", "Snow with Ash", "Vintage", "Dark Night", 
                  "Vintage Dark", "Gray Space", "Yellow Night", "Halloween", 
                  "White & Gray", "Full Gray", "Space Night", "Star Night", 
                  "Black Gray", "Dark Sky2", "Light Chocalate", 
                  "Choose According to the wallpaper"]
        self.theme_list.addItems(themes)
        right_layout.addWidget(self.theme_list)

        apply_theme_btn = QtWidgets.QPushButton("Apply Theme")
        apply_theme_btn.clicked.connect(self.on_apply_theme)
        right_layout.addWidget(apply_theme_btn)

        # Action Box
        action_box = QtWidgets.QGroupBox("Apply Wallpaper As")
        ab_layout = QtWidgets.QVBoxLayout()
        self.radio_desktop = QtWidgets.QRadioButton("Desktop")
        self.radio_lock = QtWidgets.QRadioButton("Lockscreen (i3lock)")
        self.radio_login = QtWidgets.QRadioButton("Login Screen")
        self.radio_desktop.setChecked(True)
        
        self.pos_combo = QtWidgets.QComboBox()
        self.pos_map = {
                        "Top Left": ("110:200", "100:250"),
                        "Top Center": ("710:200", "700:250"),
                        "Top Right": ("1310:200", "1300:250"),
                        "Mid Left": ("110:550", "100:600"),
                        "Center": ("710:550", "700:600"),
                        "Mid Right": ("1310:550", "1300:600"),
                        "Bottom Left": ("110:900", "100:950"),
                        "Bottom Center": ("710:900", "700:950"),
                        "Bottom Right": ("1310:900", "1300:950"),
        }
        self.pos_combo.addItems(self.pos_map.keys())
        self.pos_combo.setVisible(False)

        self.radio_lock.toggled.connect(self.pos_combo.setVisible)

        ab_layout.addWidget(self.radio_desktop)
        ab_layout.addWidget(self.radio_lock)
        ab_layout.addWidget(self.pos_combo)
        ab_layout.addWidget(self.radio_login)
        
        apply_wall_btn = QtWidgets.QPushButton("Apply Selection")
        apply_wall_btn.clicked.connect(self.on_apply_wallpaper)
        ab_layout.addWidget(apply_wall_btn)
        
        action_box.setLayout(ab_layout)
        right_layout.addWidget(action_box)

        self.splitter.addWidget(left_container)
        self.splitter.addWidget(right_container)
        main_layout.addWidget(self.splitter)

    # ------------------- Logic -------------------

    def on_load_directory(self):
        path = Path(self.dir_edit.text()).expanduser()
        if not path.is_dir(): return
        
        cache_dir = path / THUMB_CACHE_DIR_NAME
        cache_dir.mkdir(exist_ok=True)

        self._files_to_load = [f for f in path.iterdir() if f.suffix.lower() in IMAGE_EXTS]
        self._files_to_load.sort()
        self._load_index = 0
        self.thumb_list.clear()
        self.load_next_batch()

    def load_next_batch(self):
        end = min(self._load_index + BATCH_SIZE, len(self._files_to_load))
        cache_dir = Path(self.dir_edit.text()).expanduser() / THUMB_CACHE_DIR_NAME

        for i in range(self._load_index, end):
            img_path = self._files_to_load[i]
            cache_path = get_thumb_cache_path(img_path, cache_dir)
            
            pix = QtGui.QPixmap()
            if cache_path.exists() and cache_path.stat().st_mtime > img_path.stat().st_mtime:
                pix.load(str(cache_path))
            else:
                pix.load(str(img_path))
                pix = pix.scaled(THUMB_SIZE, THUMB_SIZE, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                pix.save(str(cache_path), "PNG")

            item = QtWidgets.QListWidgetItem(QtGui.QIcon(pix), "")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, str(img_path))
            self.thumb_list.addItem(item)

        self._load_index = end
        if self._load_index < len(self._files_to_load):
            QtCore.QTimer.singleShot(10, self.load_next_batch)

    # def on_selection_changed(self, current, _):
    #     if not current: return
    #     self.image_path = current.data(QtCore.Qt.ItemDataRole.UserRole)
    #     pix = QtGui.QPixmap(self.image_path)
    #     scaled = pix.scaled(self.preview_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
    #     self.preview_label.setPixmap(scaled)

    def on_selection_changed(self, current, _):
        if not current: return
        
        # 1. Get the actual absolute path from the selected item
        raw_path = current.data(QtCore.Qt.ItemDataRole.UserRole)
        
        # 2. Replace the hardcoded path with $HOME and save it to your variable
        self.image_path = raw_path.replace('/home/abhi/', '$HOME/')
        
        # 3. Use the raw_path to load the image preview!
        pix = QtGui.QPixmap(raw_path)
        scaled = pix.scaled(self.preview_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled)

    def on_apply_wallpaper(self):
        if not self.image_path: return
        
        if self.radio_desktop.isChecked():
            self.apply_desktop()
        elif self.radio_lock.isChecked():
            self.apply_lock()
        elif self.radio_login.isChecked():
            self.apply_login()

    def apply_desktop(self):
        if feh.exists():
            content = feh.read_text()
            # new_content = re.sub(r"file=.*", f"file={self.image_path}", content)
            new_content = re.sub(r"feh.*", f'''feh --no-fehbg --bg-fill "{self.image_path}"''', content)
            feh.write_text(new_content)
            # run_shell(["nitrogen", "--restore"])
            run_shell(["./.fehbg"])
        
        run_shell(["qtile", "cmd-obj", "-o", "cmd", "-f", "restart"])
        
        if COLOR_CHANGER_SH.exists():
            # Using run instead of run_shell to ensure colors update before trayer refreshes
            subprocess.run(["bash", str(COLOR_CHANGER_SH)])

        # THE FIX: Call the new function
        self.restart_trayer()

    # def apply_lock(self):
    #     tpos, dpos = self.pos_map[self.pos_combo.currentText()]
    #     # Default fallback colors
    #     color_fr, color_fr2 = "#ffffff", "#888888"

    #     # 1. Extract dynamic colors if ColorThief is available
    #     if ColorThief and self.image_path:
    #         try:
    #             ct = ColorThief(self.image_path)
    #             palette = ct.get_palette(color_count=3, quality=10)
    #             # Using first two dominant colors for fr and fr2
    #             color_fr = f"#{palette[0][0]:02X}{palette[0][1]:02X}{palette[0][2]:02X}"
    #             color_fr2 = f"#{palette[1][0]:02X}{palette[1][1]:02X}{palette[1][2]:02X}"
    #         except Exception as e:
    #             print(f"Color extraction failed: {e}")

    #     # 2. Update the lock script
    #     if LOCK_SCRIPT_PATH.exists():
    #         try:
    #             script = 2.read_text()
                
    #             # Update Paths and Positions
    #             script = re.sub(r'--image=".*?"', f'--image="{self.image_path}"', script)
    #             script = re.sub(r'--time-pos=".*?"', f'--time-pos="{tpos}"', script)
    #             script = re.sub(r'--date-pos=".*?"', f'--date-pos="{dpos}"', script)
                
    #             # Update Colors (Assuming your script uses variables or flags for colors)
    #             # If your script uses variables like fr="#hex", we update them here:
    #             script = re.sub(r'fr=".*?"', f'fr="{color_fr}"', script)
    #             script = re.sub(r'fr2=".*?"', f'fr2="{color_fr2}"', script)
                
    #             # If your i3lock command uses flags directly like --time-color, use this:
    #             # script = re.sub(r'--time-color=".*?"', f'--time-color="{color_fr}"', script)
    #             # script = re.sub(r'--date-color=".*?"', f'--date-color="{color_fr2}"', script)

    #             LOCK_SCRIPT_PATH.write_text(script)
    #             QtWidgets.QMessageBox.information(self, "Success", f"Lockscreen updated with colors: {color_fr}")
    #         except Exception as e:
    #             QtWidgets.QMessageBox.critical(self, "Error", f"Failed to write to lock script: {e}")




    def apply_lock(self):
        tpos, dpos = self.pos_map[self.pos_combo.currentText()]
        # Default fallback colors
        color_fr, color_fr2 = "#ffffff", "#888888"

        # 1. Extract dynamic colors if ColorThief is available
        if ColorThief and self.image_path:
            
            # ---> THE FIX IS HERE <---
            # Convert $HOME back to a real path just so ColorThief can open the file
            real_path = self.image_path.replace("$HOME", str(Path.home()))
            
            try:
                ct = ColorThief(real_path)
                palette = ct.get_palette(color_count=3, quality=10)
                # Using first two dominant colors for fr and fr2
                color_fr = f"#{palette[0][0]:02X}{palette[0][1]:02X}{palette[0][2]:02X}"
                color_fr2 = f"#{palette[1][0]:02X}{palette[1][1]:02X}{palette[1][2]:02X}"
            except Exception as e:
                print(f"Color extraction failed: {e}")

        # 2. Update the lock script
        if LOCK_SCRIPT_PATH.exists():
            try:
                script = LOCK_SCRIPT_PATH.read_text()
                
                # Update Paths and Positions
                script = re.sub(r'--image=".*?"', f'--image="{self.image_path}"', script)
                script = re.sub(r'--time-pos=".*?"', f'--time-pos="{tpos}"', script)
                script = re.sub(r'--date-pos=".*?"', f'--date-pos="{dpos}"', script)
                
                # Update Colors
                script = re.sub(r'fr=".*?"', f'fr="{color_fr}"', script)
                script = re.sub(r'fr2=".*?"', f'fr2="{color_fr2}"', script)

                LOCK_SCRIPT_PATH.write_text(script)
                QtWidgets.QMessageBox.information(self, "Success", f"Lockscreen updated with colors: {color_fr} & {color_fr2}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to write to lock script: {e}")




    def apply_login(self):
        cmd = ["pkexec", "cp", self.image_path, str(LOGIN_IMAGE_DEST)]
        try:
            subprocess.run(cmd, check=True)
            QtWidgets.QMessageBox.information(self, "Success", "Login wallpaper updated.")
        except:
            QtWidgets.QMessageBox.critical(self, "Error", "Permission denied.")

    def on_apply_theme(self):
        sel = self.theme_list.currentItem()
        if not sel: return
        
        theme_val = "cp.wall_color" if "wallpaper" in sel.text() else f"colors.{sel.text().lower().replace(' ', '_')}"
        
        if QTILE_FUNC_VAR.exists():
            content = QTILE_FUNC_VAR.read_text()
            new_content = re.sub(r"^co\s*=.*", f"co = {theme_val}", content, flags=re.MULTILINE)
            QTILE_FUNC_VAR.write_text(new_content)
            
            run_shell(["qtile", "cmd-obj", "-o", "cmd", "-f", "restart"])
            if COLOR_CHANGER_SH.exists():
                subprocess.run(["bash", str(COLOR_CHANGER_SH)])
            
            # THE FIX: Call the new function here too
            self.restart_trayer()


    def restart_trayer(self):
        """
        Forcefully kills trayer and restarts it after a delay 
        to ensure Qtile bar is ready.
        """
        print("==> Refreshing trayer...")
        
        # 1. Kill any existing instances immediately
        subprocess.run(["killall", "-9", "trayer"], stderr=subprocess.DEVNULL)
        
        # 2. Use a small bash script to handle the 'wait-then-start' logic
        # This keeps the GUI responsive while trayer waits to spawn
        restart_cmd = (
            "systemctl --user restart trayer"
        )
        
        # Execute the delay and start in the background
        subprocess.Popen(["bash", "-c", restart_cmd])

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()