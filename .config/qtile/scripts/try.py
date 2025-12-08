# #!/usr/bin/env python3
# """
# qtile_style_center.py

# A PyQt6 GUI to:
#  - change wallpaper (desktop, lock, login)
#  - extract two palette colors from wallpaper and update lock.sh
#  - choose and apply qtile color themes (edits func_var.py)
#  - restart qtile / restore nitrogen / run trayer.py as your original scripts did

# Adjust the path constants below if your config is in different locations.
# """

# import os
# import re
# import subprocess
# import sys
# from functools import partial
# from pathlib import Path

# from colorthief import ColorThief
# from PyQt6 import QtCore, QtGui, QtWidgets

# # ------------------------ Configuration (edit if needed) ------------------------
# HOME = Path.home()
# NITROGEN_CFG_PATH = HOME / ".config" / "nitrogen" / "bg-saved.cfg"
# LOCK_SCRIPT_PATH = HOME / ".config" / "i3lock" / "lock.sh"
# LOGIN_IMAGE_DEST = Path("/usr/share/sddm/themes/Sugar-Candy/Backgrounds/background.jpg")
# QTILE_FUNC_VAR = HOME / ".config" / "qtile" / "func_var.py"
# TRAYER_PY = HOME / ".config" / "qtile" / "trayer.py"
# COLOR_CHANGER_SH = Path.cwd() / "color_changer.sh"  # adjust if elsewhere

# # Theme list (same as your bash list)
# COLOR_OPTIONS = [
#     "Darks","Black","Snow with Ash","Vintage","Dark Night","Vintage Dark",
#     "Gray Space","Yellow Night","Halloween","White & Gray","Full Gray",
#     "Space Night","Star Night","Black Gray","Dark Sky2","Light Chocalate",
#     "Choose According to the wallpaper"
# ]

# COLOR_MAP = {
#     "Darks": "colors.darks",
#     "Black": "colors.black",
#     "Snow with Ash": "colors.snow_with_ash",
#     "Vintage": "colors.vintage",
#     "Dark Night": "colors.dark_night",
#     "Vintage Dark": "colors.vintage_dark",
#     "Gray Space": "colors.gray_space",
#     "Yellow Night": "colors.yellow_night",
#     "Halloween": "colors.halloween",
#     "White & Gray": "colors.gray_sky",
#     "Full Gray": "colors.full_gray",
#     "Space Night": "colors.space_night",
#     "Star Night": "colors.star_night",
#     "Black Gray": "colors.black_gray",
#     "Dark Sky2": "colors.dark_sky2",
#     "Light Chocalate": "colors.light_chocalate",
# }
# # -------------------------------------------------------------------------------


# def run_shell(cmd, check=False, shell=False):
#     """Run a shell command; raise on failure if check=True."""
#     if shell:
#         return subprocess.run(cmd, shell=True, check=check)
#     else:
#         return subprocess.run(cmd, check=check)


# # ----------------------------- Helper logic -----------------------------------

# def update_nitrogen_file(image_path: str):
#     p = NITROGEN_CFG_PATH
#     if not p.exists():
#         raise FileNotFoundError(f"Nitrogen config not found at {p}")
#     # Replace file= line
#     with open(p, "r") as f:
#         lines = f.readlines()
#     with open(p, "w") as f:
#         for line in lines:
#             if line.startswith("file="):
#                 f.write(f"file={image_path}\n")
#             else:
#                 f.write(line)


# def set_desktop_wallpaper(image_path: str):
#     update_nitrogen_file(image_path)
#     # Restore nitrogen and restart qtile & trayer similar to original
#     try:
#         run_shell(["nitrogen", "--restore"])
#     except Exception:
#         # not fatal — continue
#         pass

#     # original flow: restart qtile, source color_changer.sh, sleep 3, run trayer
#     # We'll attempt to run similar chained command in a shell to preserve 'source'.
#     chained = 'qtile cmd-obj -o cmd -f restart && source ./color_changer.sh && sleep 3 && "{}" &'.format(
#         TRAYER_PY
#     )
#     run_shell(chained, shell=True)
#     # slight pause then run trayer
#     run_shell('sleep 1', shell=True)
#     run_shell(f'"{TRAYER_PY}"', shell=True)


# def set_lock_image_in_script(image_path: str):
#     p = LOCK_SCRIPT_PATH
#     if not p.exists():
#         raise FileNotFoundError(f"Lock script not found: {p}")
#     with open(p, "r") as f:
#         lines = f.readlines()
#     with open(p, "w") as f:
#         for line in lines:
#             if "--image=" in line:
#                 start = line.find("--image=")
#                 before = line[:start]
#                 f.write(f'{before}--image="{image_path}" \\\n')
#             else:
#                 f.write(line)


# def set_login_wallpaper(image_path: str):
#     # Use pkexec to copy since file belongs to root location
#     # If pkexec isn't available or user doesn't have polkit privileges, this may fail.
#     run_shell(["pkexec", "cp", image_path, str(LOGIN_IMAGE_DEST)], check=True)


# def update_lock_colors_from_image(image_path: str):
#     p = LOCK_SCRIPT_PATH
#     if not p.exists():
#         raise FileNotFoundError(f"Lock script not found: {p}")
#     ct = ColorThief(image_path)
#     palette = ct.get_palette(color_count=2)
#     if len(palette) < 2:
#         raise RuntimeError("Could not extract palette from image.")
#     fr = f"#{palette[0][0]:02X}{palette[0][1]:02X}{palette[0][2]:02X}"
#     fr2 = f"#{palette[1][0]:02X}{palette[1][1]:02X}{palette[1][2]:02X}"
#     with open(p, "r") as f:
#         content = f.read()
#     content = re.sub(r'^fr="#[0-9A-Fa-f]{6}"', f'fr="{fr}"', content, flags=re.MULTILINE)
#     content = re.sub(r'^fr2="#[0-9A-Fa-f]{6}"', f'fr2="{fr2}"', content, flags=re.MULTILINE)
#     with open(p, "w") as f:
#         f.write(content)
#     return fr, fr2


# def set_qtile_theme_by_value(value: str):
#     p = QTILE_FUNC_VAR
#     if not p.exists():
#         raise FileNotFoundError(f"qtile func var not found: {p}")
#     with open(p, "r") as f:
#         content = f.read()
#     content_new = re.sub(r"^co\s*=.*$", f"co = {value}", content, flags=re.MULTILINE)
#     with open(p, "w") as f:
#         f.write(content_new)
#     # restart qtile and run color changer/trayer like before
#     run_shell(["qtile", "cmd-obj", "-o", "cmd", "-f", "restart"])
#     if COLOR_CHANGER_SH.exists():
#         run_shell(f"source \"{COLOR_CHANGER_SH}\"", shell=True)
#     # run trayer if present
#     if TRAYER_PY.exists():
#         run_shell(f'"{TRAYER_PY}"', shell=True)


# # --------------------------- PyQt6 GUI classes --------------------------------


# class ColorSwatch(QtWidgets.QFrame):
#     """Small swatch showing a color."""

#     def __init__(self, color_hex="#444444", parent=None):
#         super().__init__(parent)
#         self.setFixedSize(40, 20)
#         self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
#         self.setAutoFillBackground(True)
#         self.set_color(color_hex)

#     def set_color(self, color_hex: str):
#         pal = self.palette()
#         pal.setColor(self.backgroundRole(), QtGui.QColor(color_hex))
#         self.setPalette(pal)


# class MainWindow(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Qtile Theme & Wallpaper Center")
#         self.resize(900, 540)
#         self.image_path = None

#         # Layouts
#         main_layout = QtWidgets.QHBoxLayout(self)

#         # Left - Image preview + pick button + extracted colors
#         left = QtWidgets.QVBoxLayout()
#         self.preview_label = QtWidgets.QLabel("No image selected")
#         self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
#         self.preview_label.setFixedSize(520, 360)
#         self.preview_label.setStyleSheet("border: 1px solid #666;")
#         left.addWidget(self.preview_label, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

#         pick_btn = QtWidgets.QPushButton("Choose Image")
#         pick_btn.clicked.connect(self.on_choose_image)
#         left.addWidget(pick_btn)

#         self.swatch1 = ColorSwatch("#2C3333")
#         self.swatch2 = ColorSwatch("#444444")
#         sw_layout = QtWidgets.QHBoxLayout()
#         sw_layout.addWidget(QtWidgets.QLabel("Palette:"))
#         sw_layout.addWidget(self.swatch1)
#         sw_layout.addWidget(self.swatch2)
#         sw_layout.addStretch()
#         left.addLayout(sw_layout)

#         # Actions (Desktop/Lock/Login) and apply button
#         action_box = QtWidgets.QGroupBox("Apply Selected Image As")
#         a_layout = QtWidgets.QVBoxLayout()
#         self.radio_desktop = QtWidgets.QRadioButton("Desktop")
#         self.radio_lock = QtWidgets.QRadioButton("Lock")
#         self.radio_login = QtWidgets.QRadioButton("Login")
#         self.radio_desktop.setChecked(True)
#         a_layout.addWidget(self.radio_desktop)
#         a_layout.addWidget(self.radio_lock)
#         a_layout.addWidget(self.radio_login)

#         self.apply_btn = QtWidgets.QPushButton("Apply")
#         self.apply_btn.clicked.connect(self.on_apply_image)
#         a_layout.addWidget(self.apply_btn)
#         action_box.setLayout(a_layout)
#         left.addWidget(action_box)

#         main_layout.addLayout(left)

#         # Right - theme list and actions
#         right = QtWidgets.QVBoxLayout()
#         right.addWidget(QtWidgets.QLabel("Themes"))

#         self.theme_list = QtWidgets.QListWidget()
#         self.theme_list.addItems(COLOR_OPTIONS)
#         self.theme_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
#         right.addWidget(self.theme_list)

#         theme_buttons = QtWidgets.QHBoxLayout()
#         apply_theme_btn = QtWidgets.QPushButton("Apply Theme")
#         apply_theme_btn.clicked.connect(self.on_apply_theme)
#         theme_buttons.addWidget(apply_theme_btn)

#         apply_wall_choice_btn = QtWidgets.QPushButton("Apply 'Choose According to wallpaper'")
#         apply_wall_choice_btn.clicked.connect(self.on_apply_choose_wallpaper_theme)
#         theme_buttons.addWidget(apply_wall_choice_btn)
#         right.addLayout(theme_buttons)

#         # Info area
#         self.log = QtWidgets.QTextEdit()
#         self.log.setReadOnly(True)
#         self.log.setFixedHeight(160)
#         right.addWidget(QtWidgets.QLabel("Action Log"))
#         right.addWidget(self.log)

#         main_layout.addLayout(right)

#     # ----------------- UI helpers -----------------
#     def log_msg(self, msg: str):
#         self.log.append(msg)

#     def on_choose_image(self):
#         dlg = QtWidgets.QFileDialog(self, "Select Image")
#         dlg.setNameFilters(["Images (*.png *.jpg *.jpeg *.bmp *.webp)"])
#         dlg.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
#         if dlg.exec():
#             files = dlg.selectedFiles()
#             if files:
#                 self.load_image(files[0])

#     def load_image(self, path: str):
#         self.image_path = path
#         pix = QtGui.QPixmap(path)
#         if pix.isNull():
#             self.preview_label.setText("Cannot preview this image")
#             return
#         # scale to fit
#         scaled = pix.scaled(self.preview_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
#                             QtCore.Qt.TransformationMode.SmoothTransformation)
#         self.preview_label.setPixmap(scaled)
#         self.preview_label.setScaledContents(False)
#         self.log_msg(f"Loaded image: {path}")
#         # update palette preview (non-blocking)
#         try:
#             ct = ColorThief(path)
#             palette = ct.get_palette(color_count=2)
#             if palette and len(palette) >= 2:
#                 c1 = "#{:02X}{:02X}{:02X}".format(*palette[0])
#                 c2 = "#{:02X}{:02X}{:02X}".format(*palette[1])
#                 self.swatch1.set_color(c1)
#                 self.swatch2.set_color(c2)
#                 self.log_msg(f"Palette: {c1}, {c2}")
#         except Exception as e:
#             self.log_msg(f"Palette extraction failed: {e}")

#     def on_apply_image(self):
#         if not self.image_path:
#             QtWidgets.QMessageBox.warning(self, "No image", "Please select an image first.")
#             return
#         try:
#             if self.radio_desktop.isChecked():
#                 self.log_msg("Applying wallpaper as Desktop...")
#                 set_desktop_wallpaper(self.image_path)
#                 self.log_msg("Desktop wallpaper applied.")
#             elif self.radio_lock.isChecked():
#                 self.log_msg("Extracting colors and updating lock script...")
#                 fr, fr2 = update_lock_colors_from_image(self.image_path)
#                 self.log_msg(f"Updated lock colors fr={fr}, fr2={fr2}")
#                 set_lock_image_in_script(self.image_path)
#                 self.log_msg("Lock image and colors applied.")
#             elif self.radio_login.isChecked():
#                 self.log_msg("Copying image to login background (requires pkexec)...")
#                 set_login_wallpaper(self.image_path)
#                 self.log_msg("Login wallpaper updated.")
#         except Exception as e:
#             QtWidgets.QMessageBox.critical(self, "Error", str(e))
#             self.log_msg(f"Error: {e}")

#     def on_apply_theme(self):
#         sel = self.theme_list.currentItem()
#         if not sel:
#             QtWidgets.QMessageBox.warning(self, "No theme", "Please select a theme from the list.")
#             return
#         name = sel.text()
#         if name == "Choose According to the wallpaper":
#             # this option should set co = cp.wall_color
#             try:
#                 set_qtile_theme_by_value("cp.wall_color")
#                 self.log_msg("Applied theme: Choose According to the wallpaper -> co = cp.wall_color")
#             except Exception as e:
#                 self.log_msg(f"Theme apply error: {e}")
#                 QtWidgets.QMessageBox.critical(self, "Error", str(e))
#         else:
#             mapped = COLOR_MAP.get(name)
#             if not mapped:
#                 QtWidgets.QMessageBox.warning(self, "Unknown theme", f"No mapping for {name}")
#                 return
#             try:
#                 set_qtile_theme_by_value(mapped)
#                 self.log_msg(f"Applied theme: {name} -> {mapped}")
#             except Exception as e:
#                 self.log_msg(f"Theme apply error: {e}")
#                 QtWidgets.QMessageBox.critical(self, "Error", str(e))

#     def on_apply_choose_wallpaper_theme(self):
#         # Shortcut: apply cp.wall_color and source color_changer.sh
#         try:
#             set_qtile_theme_by_value("cp.wall_color")
#             if COLOR_CHANGER_SH.exists():
#                 run_shell(f"source \"{COLOR_CHANGER_SH}\"", shell=True)
#             if TRAYER_PY.exists():
#                 run_shell(f'"{TRAYER_PY}"', shell=True)
#             self.log_msg("Applied cp.wall_color theme and ran color_changer/trayer.")
#         except Exception as e:
#             self.log_msg(f"Error: {e}")
#             QtWidgets.QMessageBox.critical(self, "Error", str(e))


# # --------------------------- Entry point -------------------------------------

# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     w = MainWindow()
#     w.show()
#     sys.exit(app.exec())


# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
"""
qtile_style_center_gallery_fast.py

- Gallery loads thumbnails in small batches so the UI doesn't freeze.
- Color palette preview is shown ONLY when "Lock" is selected (or when applying Lock).
- Palette extraction runs in a background worker.
- Keeps apply behaviors: Desktop (nitrogen), Lock (update lock.sh + palette), Login (pkexec copy).
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List

from colorthief import ColorThief
from PyQt6 import QtCore, QtGui, QtWidgets

# ------------------------ Config (edit if needed) ------------------------
HOME = Path.home()
DEFAULT_WALL_DIR = HOME / "Pictures" / "walls"
NITROGEN_CFG_PATH = HOME / ".config" / "nitrogen" / "bg-saved.cfg"
LOCK_SCRIPT_PATH = HOME / ".config" / "i3lock" / "lock.sh"
LOGIN_IMAGE_DEST = Path("/usr/share/sddm/themes/Sugar-Candy/Backgrounds/background.jpg")
QTILE_FUNC_VAR = HOME / ".config" / "qtile" / "func_var.py"
TRAYER_PY = HOME / ".config" / "qtile" / "trayer.py"
COLOR_CHANGER_SH = Path.cwd() / "color_changer.sh"
THUMB_SIZE = 128
BATCH_SIZE = 12     # number of thumbnails processed per event loop tick
# -----------------------------------------------------------------------

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


def run_shell(cmd, check=False, shell=False):
    if shell:
        return subprocess.run(cmd, shell=True, check=check)
    else:
        return subprocess.run(cmd, check=check)


# ------------------------- Non-GUI helpers ---------------------------------

def update_nitrogen_file(image_path: str):
    p = NITROGEN_CFG_PATH
    if not p.exists():
        raise FileNotFoundError(f"Nitrogen config not found at {p}")
    with open(p, "r") as f:
        lines = f.readlines()
    with open(p, "w") as f:
        for line in lines:
            if line.startswith("file="):
                f.write(f"file={image_path}\n")
            else:
                f.write(line)


def set_desktop_wallpaper(image_path: str):
    update_nitrogen_file(image_path)
    try:
        run_shell(["nitrogen", "--restore"])
    except Exception:
        pass
    chained = 'qtile cmd-obj -o cmd -f restart && source ./color_changer.sh && sleep 3 && "{}" &'.format(
        TRAYER_PY
    )
    run_shell(chained, shell=True)
    run_shell('sleep 1', shell=True)
    run_shell(f'"{TRAYER_PY}"', shell=True)


def set_lock_image_in_script(image_path: str):
    p = LOCK_SCRIPT_PATH
    if not p.exists():
        raise FileNotFoundError(f"Lock script not found: {p}")
    with open(p, "r") as f:
        lines = f.readlines()
    with open(p, "w") as f:
        for line in lines:
            if "--image=" in line:
                start = line.find("--image=")
                before = line[:start]
                f.write(f'{before}--image="{image_path}" \\\n')
            else:
                f.write(line)


def set_login_wallpaper(image_path: str):
    run_shell(["pkexec", "cp", image_path, str(LOGIN_IMAGE_DEST)], check=True)


def update_lock_colors_from_image(image_path: str):
    """
    Extracts two palette colors using ColorThief and updates LOCK_SCRIPT_PATH
    Returns (fr, fr2).
    """
    p = LOCK_SCRIPT_PATH
    if not p.exists():
        raise FileNotFoundError(f"Lock script not found: {p}")
    ct = ColorThief(image_path)
    palette = ct.get_palette(color_count=2)
    if len(palette) < 2:
        raise RuntimeError("Could not extract palette from image.")
    fr = f"#{palette[0][0]:02X}{palette[0][1]:02X}{palette[0][2]:02X}"
    fr2 = f"#{palette[1][0]:02X}{palette[1][1]:02X}{palette[1][2]:02X}"
    with open(p, "r") as f:
        content = f.read()
    content = re.sub(r'^fr="#[0-9A-Fa-f]{6}"', f'fr="{fr}"', content, flags=re.MULTILINE)
    content = re.sub(r'^fr2="#[0-9A-Fa-f]{6}"', f'fr2="{fr2}"', content, flags=re.MULTILINE)
    with open(p, "w") as f:
        f.write(content)
    return fr, fr2


def set_qtile_theme_by_value(value: str):
    p = QTILE_FUNC_VAR
    if not p.exists():
        raise FileNotFoundError(f"qtile func var not found: {p}")
    with open(p, "r") as f:
        content = f.read()
    content_new = re.sub(r"^co\s*=.*$", f"co = {value}", content, flags=re.MULTILINE)
    with open(p, "w") as f:
        f.write(content_new)
    run_shell(["qtile", "cmd-obj", "-o", "cmd", "-f", "restart"])
    if COLOR_CHANGER_SH.exists():
        run_shell(f"source \"{COLOR_CHANGER_SH}\"", shell=True)
    if TRAYER_PY.exists():
        run_shell(f'"{TRAYER_PY}"', shell=True)


# ---------------------- Background worker (palette) -------------------------

class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(tuple)  # will emit (fr, fr2, image_path)
    error = QtCore.pyqtSignal(str)


class PaletteWorker(QtCore.QRunnable):
    """
    Extract palette (colorthief) in background and emit result.
    """

    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path
        self.signals = WorkerSignals()

    def run(self):
        try:
            fr, fr2 = update_lock_colors_from_image(self.image_path)
            self.signals.finished.emit((fr, fr2, self.image_path))
        except Exception as e:
            self.signals.error.emit(str(e))


# --------------------------- GUI components ---------------------------------

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qtile Theme & Wallpaper Center (Fast Gallery)")
        self.resize(1000, 600)
        self.image_path = None
        self._files_to_load: List[Path] = []
        self._load_index = 0

        # Thread pool for palette worker
        self.pool = QtCore.QThreadPool.globalInstance()

        # Layouts
        main_layout = QtWidgets.QHBoxLayout(self)

        # Left side: preview, thumbnails, dir controls, apply
        left = QtWidgets.QVBoxLayout()

        self.preview_label = QtWidgets.QLabel("No image selected")
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedSize(640, 360)
        self.preview_label.setStyleSheet("border: 1px solid #666; background: #eee;")
        left.addWidget(self.preview_label, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

        # Thumbnail list (icon mode)
        self.thumb_list = QtWidgets.QListWidget()
        self.thumb_list.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.thumb_list.setIconSize(QtCore.QSize(THUMB_SIZE, THUMB_SIZE))
        self.thumb_list.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.thumb_list.setMovement(QtWidgets.QListView.Movement.Static)
        self.thumb_list.setSpacing(8)
        self.thumb_list.setFlow(QtWidgets.QListView.Flow.LeftToRight)
        self.thumb_list.setWrapping(True)
        self.thumb_list.setFixedHeight(THUMB_SIZE + 40)
        self.thumb_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.thumb_list.itemClicked.connect(self.on_thumbnail_clicked)
        self.thumb_list.itemActivated.connect(self.on_thumbnail_activated)
        left.addWidget(self.thumb_list)

        # Directory controls
        dir_layout = QtWidgets.QHBoxLayout()
        self.dir_edit = QtWidgets.QLineEdit(str(DEFAULT_WALL_DIR))
        load_btn = QtWidgets.QPushButton("Load Directory")
        load_btn.clicked.connect(self.on_load_directory)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(load_btn)
        left.addLayout(dir_layout)

        # Palette area (hidden unless Lock is selected)
        pal_layout = QtWidgets.QHBoxLayout()
        self.palette_label = QtWidgets.QLabel("Palette:")
        self.palette_label.setVisible(False)
        pal_layout.addWidget(self.palette_label)
        self.swatch1 = QtWidgets.QFrame()
        self.swatch1.setFixedSize(40, 20)
        self.swatch1.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.swatch1.setVisible(False)
        self.swatch2 = QtWidgets.QFrame()
        self.swatch2.setFixedSize(40, 20)
        self.swatch2.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.swatch2.setVisible(False)
        pal_layout.addWidget(self.swatch1)
        pal_layout.addWidget(self.swatch2)
        pal_layout.addStretch()
        left.addLayout(pal_layout)

        # Apply actions
        action_box = QtWidgets.QGroupBox("Apply Selected Image As")
        a_layout = QtWidgets.QVBoxLayout()
        self.radio_desktop = QtWidgets.QRadioButton("Desktop")
        self.radio_lock = QtWidgets.QRadioButton("Lock")
        self.radio_login = QtWidgets.QRadioButton("Login")
        self.radio_desktop.setChecked(True)
        a_layout.addWidget(self.radio_desktop)
        a_layout.addWidget(self.radio_lock)
        a_layout.addWidget(self.radio_login)

        # toggle palette visibility when lock toggled
        self.radio_desktop.toggled.connect(self.on_action_toggled)
        self.radio_lock.toggled.connect(self.on_action_toggled)
        self.radio_login.toggled.connect(self.on_action_toggled)

        apply_btn = QtWidgets.QPushButton("Apply")
        apply_btn.clicked.connect(self.on_apply_image)
        a_layout.addWidget(apply_btn)
        action_box.setLayout(a_layout)
        left.addWidget(action_box)

        main_layout.addLayout(left, stretch=3)

        # Right side: themes list & log
        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel("Themes"))

        color_options = [
            "Darks","Black","Snow with Ash","Vintage","Dark Night","Vintage Dark",
            "Gray Space","Yellow Night","Halloween","White & Gray","Full Gray",
            "Space Night","Star Night","Black Gray","Dark Sky2","Light Chocalate",
            "Choose According to the wallpaper"
        ]
        self.theme_list = QtWidgets.QListWidget()
        self.theme_list.addItems(color_options)
        self.theme_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        right.addWidget(self.theme_list)

        theme_buttons = QtWidgets.QHBoxLayout()
        apply_theme_btn = QtWidgets.QPushButton("Apply Theme")
        apply_theme_btn.clicked.connect(self.on_apply_theme)
        theme_buttons.addWidget(apply_theme_btn)

        apply_wall_choice_btn = QtWidgets.QPushButton("Apply 'Choose Acc. to wallpaper'")
        apply_wall_choice_btn.clicked.connect(self.on_apply_choose_wallpaper_theme)
        theme_buttons.addWidget(apply_wall_choice_btn)
        right.addLayout(theme_buttons)

        right.addWidget(QtWidgets.QLabel("Action Log"))
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(200)
        right.addWidget(self.log)

        main_layout.addLayout(right, stretch=1)

    # ------------------- UI helpers ----------------------------------------

    def log_msg(self, msg: str):
        self.log.append(msg)

    def set_swatch_color(self, frame: QtWidgets.QFrame, color_hex: str):
        pal = frame.palette()
        pal.setColor(frame.backgroundRole(), QtGui.QColor(color_hex))
        frame.setPalette(pal)
        frame.setAutoFillBackground(True)

    # ------------------- Gallery loading (non-blocking batches) --------------

    def on_load_directory(self):
        dirpath = Path(self.dir_edit.text()).expanduser()
        if not dirpath.exists() or not dirpath.is_dir():
            QtWidgets.QMessageBox.warning(self, "Invalid folder", "Please enter a valid wallpapers folder path.")
            return
        files = [p for p in dirpath.iterdir() if p.suffix.lower() in IMAGE_EXTS and p.is_file()]
        files.sort()
        self._files_to_load = files
        self._load_index = 0
        self.thumb_list.clear()
        self.log_msg(f"Scanning {len(files)} images...")
        # start the incremental loader
        QtCore.QTimer.singleShot(0, self._process_thumbnail_batch)

    def _process_thumbnail_batch(self):
        end = min(self._load_index + BATCH_SIZE, len(self._files_to_load))
        for i in range(self._load_index, end):
            p = self._files_to_load[i]
            pix = QtGui.QPixmap(str(p))
            if pix.isNull():
                continue
            icon = QtGui.QIcon(pix.scaled(THUMB_SIZE, THUMB_SIZE,
                                          QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                          QtCore.Qt.TransformationMode.SmoothTransformation))
            item = QtWidgets.QListWidgetItem(icon, p.name)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, str(p))
            self.thumb_list.addItem(item)
        self._load_index = end
        self.log_msg(f"Loaded thumbnails: {self._load_index}/{len(self._files_to_load)}")
        if self._load_index < len(self._files_to_load):
            # schedule next batch
            QtCore.QTimer.singleShot(10, self._process_thumbnail_batch)
        else:
            self.log_msg("Gallery load complete.")

    # ------------------- Thumbnail events & preview -------------------------

    def on_thumbnail_clicked(self, item: QtWidgets.QListWidgetItem):
        path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if path:
            self.load_image_preview(path)

    def on_thumbnail_activated(self, item: QtWidgets.QListWidgetItem):
        # double-click: preview and apply immediately
        path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if path:
            self.load_image_preview(path)
            self.apply_image_at_path(path)

    def load_image_preview(self, path: str):
        self.image_path = path
        pix = QtGui.QPixmap(path)
        if pix.isNull():
            self.preview_label.setText("Cannot preview this image")
            return
        scaled = pix.scaled(self.preview_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                            QtCore.Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled)
        self.preview_label.setScaledContents(False)
        self.log_msg(f"Loaded image: {path}")

        # If Lock is selected, run palette extraction worker (background)
        if self.radio_lock.isChecked():
            self.log_msg("Extracting lock palette (background)...")
            worker = PaletteWorker(path)
            worker.signals.finished.connect(self.on_palette_extracted)
            worker.signals.error.connect(lambda e: self.log_msg(f"Palette error: {e}"))
            self.pool.start(worker)

    # ------------------- Palette handlers -----------------------------------

    def on_palette_extracted(self, result_tuple):
        fr, fr2, image_path = result_tuple
        # show palette only if still relevant (lock selected and same image)
        if self.radio_lock.isChecked() and self.image_path == image_path:
            self.palette_label.setVisible(True)
            self.swatch1.setVisible(True)
            self.swatch2.setVisible(True)
            self.set_swatch_color(self.swatch1, fr)
            self.set_swatch_color(self.swatch2, fr2)
            self.log_msg(f"Palette: {fr}, {fr2}")
        else:
            # update lock script silently (still done by worker), but don't show swatches
            self.log_msg(f"Palette extracted for {image_path} (hidden)")

    # ------------------- Apply logic ----------------------------------------

    def apply_image_at_path(self, path: str):
        try:
            if self.radio_desktop.isChecked():
                self.log_msg("Applying wallpaper as Desktop...")
                set_desktop_wallpaper(path)
                self.log_msg("Desktop wallpaper applied.")
            elif self.radio_lock.isChecked():
                self.log_msg("Applying as Lock: extracting & updating lock script...")
                # run palette worker and update lock script in background; but also update swatches when done
                worker = PaletteWorker(path)
                worker.signals.finished.connect(self.on_palette_extracted)
                worker.signals.error.connect(lambda e: self.log_msg(f"Palette error: {e}"))
                self.pool.start(worker)
                # write image path to lock script (immediate)
                set_lock_image_in_script(path)
                self.log_msg("Lock image path written. Palette update will complete shortly.")
            elif self.radio_login.isChecked():
                self.log_msg("Copying image to login background (requires pkexec)...")
                set_login_wallpaper(path)
                self.log_msg("Login wallpaper updated.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            self.log_msg(f"Error: {e}")

    def on_apply_image(self):
        if not self.image_path:
            QtWidgets.QMessageBox.warning(self, "No image", "Please select an image (from gallery) first.")
            return
        self.apply_image_at_path(self.image_path)

    # ------------------- Theme handlers ------------------------------------

    def on_apply_theme(self):
        sel = self.theme_list.currentItem()
        if not sel:
            QtWidgets.QMessageBox.warning(self, "No theme", "Please select a theme.")
            return
        name = sel.text()
        if name == "Choose According to the wallpaper":
            try:
                set_qtile_theme_by_value("cp.wall_color")
                self.log_msg("Applied theme: cp.wall_color")
            except Exception as e:
                self.log_msg(f"Theme apply error: {e}")
        else:
            mapping = {
                "Darks": "colors.darks", "Black": "colors.black", "Snow with Ash": "colors.snow_with_ash",
                "Vintage": "colors.vintage", "Dark Night": "colors.dark_night", "Vintage Dark": "colors.vintage_dark",
                "Gray Space": "colors.gray_space", "Yellow Night": "colors.yellow_night", "Halloween": "colors.halloween",
                "White & Gray": "colors.gray_sky", "Full Gray": "colors.full_gray", "Space Night": "colors.space_night",
                "Star Night": "colors.star_night", "Black Gray": "colors.black_gray", "Dark Sky2": "colors.dark_sky2",
                "Light Chocalate": "colors.light_chocalate"
            }.get(name)
            if not mapping:
                QtWidgets.QMessageBox.warning(self, "Unknown theme", f"No mapping for {name}")
                return
            try:
                set_qtile_theme_by_value(mapping)
                self.log_msg(f"Applied theme: {name} -> {mapping}")
            except Exception as e:
                self.log_msg(f"Theme apply error: {e}")

    def on_apply_choose_wallpaper_theme(self):
        try:
            set_qtile_theme_by_value("cp.wall_color")
            if COLOR_CHANGER_SH.exists():
                run_shell(f"source \"{COLOR_CHANGER_SH}\"", shell=True)
            if TRAYER_PY.exists():
                run_shell(f'"{TRAYER_PY}"', shell=True)
            self.log_msg("Applied cp.wall_color theme and ran color_changer/trayer.")
        except Exception as e:
            self.log_msg(f"Error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    # ------------------- Radio toggle handler --------------------------------

    def on_action_toggled(self, _=None):
        # show palette controls only when Lock is selected
        lock_selected = self.radio_lock.isChecked()
        self.palette_label.setVisible(lock_selected)
        self.swatch1.setVisible(lock_selected)
        self.swatch2.setVisible(lock_selected)
        if lock_selected and self.image_path:
            # trigger palette extraction for currently previewed image
            self.log_msg("Lock selected: extracting palette for current preview...")
            worker = PaletteWorker(self.image_path)
            worker.signals.finished.connect(self.on_palette_extracted)
            worker.signals.error.connect(lambda e: self.log_msg(f"Palette error: {e}"))
            self.pool.start(worker)

# --------------------------- Entry point -------------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
