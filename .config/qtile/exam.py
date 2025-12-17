#!/usr/bin/env python3
"""
qtile_style_center_fast_lockpos_without_palette.py
(Palette extraction removed)

- Fast gallery (batch thumbnail loading)
- Safe lock.sh updater with backups and lock clock position chooser
- Apply behaviors: Desktop (nitrogen), Lock (update image + time/date pos + default fr/fr2), Login (pkexec copy)

Install:
  pip install PyQt6
Run:
  chmod +x qtile_style_center_fast_lockpos_without_palette.py
  ./qtile_style_center_fast_lockpos_without_palette.py
Auther: Abhishek Mishra(https://github.com/gmkng01)
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Tuple

from PyQt6 import QtCore, QtGui, QtWidgets

# ------------------------ Config (edit if needed) ------------------------
HOME = Path.home()
DEFAULT_WALL_DIR = HOME / "Pictures" / "walls"
NITROGEN_CFG_PATH = HOME / ".config" / "nitrogen" / "bg-saved.cfg"
LOCK_SCRIPT_PATH = HOME / ".config" / "i3lock" / "lock.sh"
LOGIN_IMAGE_DEST = Path("/usr/share/pixmaps/background.jpeg")
QTILE_FUNC_VAR = HOME / ".config" / "qtile" / "func_var.py"
TRAYER_PY = HOME / ".config" / "qtile" / "trayer.py"
COLOR_CHANGER_SH = Path.cwd() / "color_changer.sh"
THUMB_SIZE = 158
BATCH_SIZE = 12     # thumbnails per batch

# UI appearance (change these)
FONT_FAMILY = "JetBrainsMono Nerd Font"   # <-- put the font you want here (e.g. "Fira Code", "JetBrains Mono", "Sans")
FONT_SIZE = 10              # global font size in pts

# Dark stylesheet used for the whole application. Tweak colors if you like.
DARK_STYLESHEET = """
/* Base window */
QWidget {
    background-color: #101217;
    color: #d7dde6;
    font-family: "%FONT%";
    font-size: %FONTSIZE%pt;
}

/* Preview area */
QLabel {
    color: #d7dde6;
}

/* List widgets and selection */
QListWidget {
    background-color: #0f1418;
    border: 1px solid #22272b;
    selection-background-color: #2a3440;
    selection-color: #e6eef6;
}

/* Buttons */
QPushButton {
    background-color: #1a2024;
    color: #d7dde6;
    border: 1px solid #2b3338;
    padding: 6px 10px;
    border-radius: 6px;
}
QPushButton:hover { background-color: #232a2e; }
QPushButton:pressed { background-color: #0f1418; }

/* Group boxes */
QGroupBox {
    border: 1px solid #23292d;
    margin-top: 6px;
}

/* TextEdit (log) */
QTextEdit {
    background-color: #0c1014;
    border: 1px solid #191f23;
    color: #cfe6ff;
}

/* ComboBox */
QComboBox {
    background-color: #111418;
    border: 1px solid #22272b;
    padding: 4px;
}

/* Scrollbar */
QScrollBar:vertical {
    background: #0d1114;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #1d2529;
    min-height: 20px;
}

/* Frames used as swatches - give them a border so they pop */
QFrame {
    border: 1px solid #30363a;
    border-radius: 2px;
}
""".replace("%FONT%", FONT_FAMILY).replace("%FONTSIZE%", str(FONT_SIZE))
# -----------------------------------------------------------------------



# -----------------------------------------------------------------------

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp"}


def run_shell(cmd, check=False, shell=False):
    if shell:
        return subprocess.run(cmd, shell=True, check=check)
    else:
        return subprocess.run(cmd, check=check)


# --------------------------- Safe lock updater -----------------------------

def _make_backup(path: Path) -> Path:
    if not path.exists():
        return None
    now = time.strftime("%Y%m%d-%H%M%S")
    bak = path.with_suffix(path.suffix + f".bak-{now}")
    shutil.copy2(path, bak)
    return bak

def _atomic_replace(target: Path, new_content: str):
    dirpath = target.parent
    fd, tmp_path = tempfile.mkstemp(prefix=target.name + ".", dir=str(dirpath))
    os.close(fd)
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    try:
        st = target.stat()
        os.chmod(tmp_path, st.st_mode)
    except FileNotFoundError:
        os.chmod(tmp_path, 0o755)
    Path(tmp_path).replace(target)

def safe_update_lock_script(image_path: str, time_pos: str = None, date_pos: str = None, fr: str = None, fr2: str = None) -> Path:
    """
    Backup and atomically update lock.sh with:
      --image="..."
      --time-pos="x:y"
      --date-pos="x:y"
    Also update fr/fr2 variables if provided.
    Returns backup path or None.
    """
    p = LOCK_SCRIPT_PATH
    if not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)

    bak = _make_backup(p)
    content = ""
    if p.exists():
        content = p.read_text(encoding="utf-8")
    else:
        # minimal template if missing
        content = "#!/usr/bin/env bash\nfr=\"#2C3333\"\nfr2=\"#444444\"\n\n# i3lock placeholder\ni3lock --image=\"\" \n"

    # fr/fr2 replace or prepend
    if fr:
        if re.search(r'^\s*fr\s*=.*$', content, flags=re.MULTILINE):
            content = re.sub(r'^\s*fr\s*=.*$', f'fr="{fr}"', content, flags=re.MULTILINE)
        else:
            content = f'fr="{fr}"\n' + content
    if fr2:
        if re.search(r'^\s*fr2\s*=.*$', content, flags=re.MULTILINE):
            content = re.sub(r'^\s*fr2\s*=.*$', f'fr2="{fr2}"', content, flags=re.MULTILINE)
        else:
            content = f'fr2="{fr2}"\n' + content

    # Replace/add --image
    if '--image=' in content:
        content = re.sub(r'--image="[^"]*"', f'--image="{image_path}"', content)
    else:
        m = re.search(r'(^[^#\n]*\bi3lock\b[^\n]*)', content, flags=re.MULTILINE)
        if m:
            line = m.group(1)
            new_line = re.sub(r'\bi3lock\b', f'i3lock --image="{image_path}"', line, count=1)
            content = content.replace(line, new_line, 1)
        else:
            content += f'\ni3lock --image="{image_path}"\n'

    # Replace/add time-pos
    if time_pos:
        if '--time-pos=' in content:
            content = re.sub(r'--time-pos="[^"]*"', f'--time-pos="{time_pos}"', content)
        else:
            m = re.search(r'(^[^#\n]*\bi3lock\b[^\n]*)', content, flags=re.MULTILINE)
            if m:
                line = m.group(1)
                new_line = re.sub(r'\bi3lock\b', f'i3lock --time-pos="{time_pos}"', line, count=1)
                content = content.replace(line, new_line, 1)
            else:
                content += f'\ni3lock --time-pos="{time_pos}"\n'

    # Replace/add date-pos
    if date_pos:
        if '--date-pos=' in content:
            content = re.sub(r'--date-pos="[^"]*"', f'--date-pos="{date_pos}"', content)
        else:
            m = re.search(r'(^[^#\n]*\bi3lock\b[^\n]*)', content, flags=re.MULTILINE)
            if m:
                line = m.group(1)
                new_line = re.sub(r'\bi3lock\b', f'i3lock --date-pos="{date_pos}"', line, count=1)
                content = content.replace(line, new_line, 1)
            else:
                content += f'\ni3lock --date-pos="{date_pos}"\n'

    _atomic_replace(p, content)
    return bak

# --------------------------- GUI (fast gallery) -----------------------------

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qtile Theme & Wallpaper Center")
        self.resize(1000, 600)
        self.image_path = None
        self._files_to_load: List[Path] = []
        self._load_index = 0
        self.pool = QtCore.QThreadPool.globalInstance()

        # 1. Create the main QSplitter (Horizontal)
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        
        # 2. Create the main window layout to hold the splitter
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.main_splitter)

        # --- Left Section Container (NOW USING A VERTICAL SPLITTER) ---
        
        # Create the vertical splitter for the left side
        left_v_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        
        # A. Preview Widget
        preview_widget = QtWidgets.QWidget()
        preview_layout = QtWidgets.QVBoxLayout(preview_widget)
        
        self.preview_label = QtWidgets.QLabel("No image selected")
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(300, 200) # Use minimum size instead of fixed
        self.preview_label.setStyleSheet("border: 1px solid #666; background: #eee;")
        preview_layout.addWidget(self.preview_label)
        
        # B. Thumbnail Gallery Widget
        thumb_widget = QtWidgets.QWidget()
        thumb_layout = QtWidgets.QVBoxLayout(thumb_widget)
        
        self.thumb_list = QtWidgets.QListWidget()
        self.thumb_list.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.thumb_list.setIconSize(QtCore.QSize(THUMB_SIZE, THUMB_SIZE))
        self.thumb_list.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.thumb_list.setMovement(QtWidgets.QListView.Movement.Static)
        self.thumb_list.setSpacing(8)
        self.thumb_list.setFlow(QtWidgets.QListView.Flow.LeftToRight)
        self.thumb_list.setWrapping(True)
        # Remove fixed height (or set to small minimum)
        self.thumb_list.setMinimumHeight(THUMB_SIZE + 20)
        self.thumb_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.thumb_list.itemClicked.connect(self.on_thumbnail_clicked)
        self.thumb_list.itemActivated.connect(self.on_thumbnail_activated)
        thumb_layout.addWidget(self.thumb_list)

        # C. Directory Bar Widget
        dir_widget = QtWidgets.QWidget()
        dir_layout = QtWidgets.QHBoxLayout(dir_widget)
        self.dir_edit = QtWidgets.QLineEdit(str(DEFAULT_WALL_DIR))
        self.dir_edit.setPlaceholderText("Wallpaper directory")
        dir_layout.addWidget(self.dir_edit)
        
        # Add the three widgets to the vertical splitter
        left_v_splitter.addWidget(preview_widget)
        left_v_splitter.addWidget(thumb_widget)
        left_v_splitter.addWidget(dir_widget) # Directory widget will take minimal space
        
        # Set initial sizes for the vertical split
        left_v_splitter.setSizes([450, 150, 50]) 

        QtCore.QTimer.singleShot(0, self.on_load_directory)

        self._dir_reload_timer = QtCore.QTimer(self)
        self._dir_reload_timer.setSingleShot(True)
        self._dir_reload_timer.timeout.connect(self.on_load_directory)

        self.dir_edit.textChanged.connect(
            lambda: self._dir_reload_timer.start(500)
        )
        
        # Add the entire left vertical splitter to the main horizontal splitter
        self.main_splitter.addWidget(left_v_splitter)
        
        # --- Right Section Container ---
        right_widget = QtWidgets.QWidget()
        right = QtWidgets.QVBoxLayout(right_widget)
        
        # --- THEMES SECTION ---
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
        right.addWidget(self.theme_list, stretch=1) 

        theme_buttons = QtWidgets.QHBoxLayout()
        apply_theme_btn = QtWidgets.QPushButton("Apply Theme")
        apply_theme_btn.clicked.connect(self.on_apply_theme)
        theme_buttons.addWidget(apply_theme_btn)
        apply_wall_choice_btn = QtWidgets.QPushButton("Apply 'Choose Acc. to wallpaper'")
        apply_wall_choice_btn.clicked.connect(self.on_apply_choose_wallpaper_theme)
        theme_buttons.addWidget(apply_wall_choice_btn)
        right.addLayout(theme_buttons)
        # --- END THEMES SECTION ---
        
        # Add a spacer here to push the action box down
        right.addStretch(1) 
        
        # --- ACTION GROUP (APPLY SELECTED IMAGE AS) SECTION ---
        action_box = QtWidgets.QGroupBox("Apply Selected Image As")
        a_layout = QtWidgets.QVBoxLayout()
        self.radio_desktop = QtWidgets.QRadioButton("Desktop")
        self.radio_lock = QtWidgets.QRadioButton("Lock")
        self.radio_login = QtWidgets.QRadioButton("Login")
        self.radio_desktop.setChecked(True)
        a_layout.addWidget(self.radio_desktop)
        a_layout.addWidget(self.radio_lock)
        a_layout.addWidget(self.radio_login)

        # -----------------------------------------------------------
        # NEW: Create a container widget for the lock position chooser
        # -----------------------------------------------------------
        self.pos_container = QtWidgets.QWidget()
        pos_layout = QtWidgets.QHBoxLayout(self.pos_container)
        pos_layout.setContentsMargins(0, 0, 0, 0) # Use zero margins for cleaner integration

        pos_layout.addWidget(QtWidgets.QLabel("Lock clock position:"))
        self.pos_combo = QtWidgets.QComboBox()
        pos_options = [
                    ("top_left",    "110:200",  "100:250"),
                    ("top_center",  "710:200",  "700:250"),
                    ("top_right",   "1310:200", "1300:250"),
                    ("mid_left",    "110:550",  "100:600"),
                    ("mid_center",  "710:550",  "700:600"),
                    ("mid_right",   "1310:550", "1300:600"),
                    ("bottom_left", "110:900",  "100:950"),
                    ("bottom_center","710:900", "700:950"),
                    ("bottom_right","1310:900", "1300:950"),
        ]
        for name, tpos, dpos in pos_options:
            self.pos_combo.addItem(name)
            idx = self.pos_combo.count() - 1
            self.pos_combo.setItemData(idx, (tpos, dpos))
            
        pos_layout.addWidget(self.pos_combo)
        
        # Add the new container to the Action box layout
        a_layout.addWidget(self.pos_container)

        apply_btn = QtWidgets.QPushButton("Apply")
        apply_btn.clicked.connect(self.on_apply_image)
        a_layout.addWidget(apply_btn)
        action_box.setLayout(a_layout)
        right.addWidget(action_box)
        # --- END ACTION GROUP SECTION ---
        
        # Add the right container to the main horizontal splitter
        self.main_splitter.addWidget(right_widget)

        # Set initial sizes for the main horizontal split
        self.main_splitter.setSizes([750, 250]) 

        # radio toggles (must be connected after they are initialized)
        self.radio_desktop.toggled.connect(self.on_action_toggled)
        self.radio_lock.toggled.connect(self.on_action_toggled)
        self.radio_login.toggled.connect(self.on_action_toggled)
        
        # Ensure initial state is correct (Lock position hidden)
        self.on_action_toggled(False)
        
        # Connect the size changed event of the preview label to re-scale the image
        self.preview_label.resizeEvent = self.on_preview_label_resized


    # --- New method to handle preview image resizing ---
    def on_preview_label_resized(self, event):
        """Re-scales the preview image when the label container is resized."""
        if self.image_path:
            pix = QtGui.QPixmap(self.image_path)
            if not pix.isNull():
                scaled = pix.scaled(self.preview_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                    QtCore.Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled)
        # Call the base class implementation
        super(QtWidgets.QLabel, self.preview_label).resizeEvent(event)
        
    # ------------------- UI helpers ----------------------------------------
    
    def log_msg(self, msg: str):
        # self.log.append(msg)
        pass

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
            item = QtWidgets.QListWidgetItem()
            item.setIcon(icon)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, str(p))

            self.thumb_list.addItem(item)
        self._load_index = end
        self.log_msg(f"Loaded thumbnails: {self._load_index}/{len(self._files_to_load)}")
        if self._load_index < len(self._files_to_load):
            QtCore.QTimer.singleShot(10, self._process_thumbnail_batch)
        else:
            self.log_msg("Gallery load complete.")

    # ------------------- Thumbnail events & preview -------------------------

    def on_thumbnail_clicked(self, item: QtWidgets.QListWidgetItem):
        path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if path:
            self.load_image_preview(path)

    def on_thumbnail_activated(self, item: QtWidgets.QListWidgetItem):
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
        
        # Scaled dynamically using the label's current size
        scaled = pix.scaled(self.preview_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                            QtCore.Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled)
        self.log_msg(f"Loaded image: {path}")

    # ------------------- Apply logic ----------------------------------------
    
    def apply_image_at_path(self, path: str):
        try:
            if self.radio_desktop.isChecked():
                self.log_msg("Applying wallpaper as Desktop...")
                self._apply_desktop(path)
                self.log_msg("Desktop wallpaper applied.")
            elif self.radio_lock.isChecked():
                self.log_msg("Applying as Lock: backing up and updating lock script...")
                idx = self.pos_combo.currentIndex()
                tpos, dpos = self.pos_combo.itemData(idx) if idx >= 0 else (None, None)
                
                # Use default neutral colors for fr/fr2 since palette extraction is removed
                fr = "#2C3333"
                fr2 = "#444444" 
                
                bak = safe_update_lock_script(path, time_pos=tpos, date_pos=dpos, fr=fr, fr2=fr2)
                self.log_msg(f"Lock script updated with default colors. Backup: {bak}")
            elif self.radio_login.isChecked():
                self.log_msg("Copying image to login background (requires privilege escalation)...")
                self.set_login_wallpaper(path)
                self.log_msg("Login wallpaper handling done.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            self.log_msg(f"Error: {e}")

    def on_apply_image(self):
        if not self.image_path:
            QtWidgets.QMessageBox.warning(self, "No image", "Please select an image (from gallery) first.")
            return
        self.apply_image_at_path(self.image_path)

    def _apply_desktop(self, image_path: str):
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

    # ------------------- Login wallpaper (safe copy + perms + optional restart) -

    def set_login_wallpaper(self, image_path: str, dest: Path = LOGIN_IMAGE_DEST):
        """
        Try pkexec -> sudo -> direct copy to place the login background.
        Set sane perms (root:root, 0644). Optionally prompt to restart sddm.
        """
        if not Path(image_path).exists():
            QtWidgets.QMessageBox.critical(self, "Error", f"Image not found: {image_path}")
            self.log_msg(f"Login copy failed: source missing {image_path}")
            return

        self.log_msg(f"Attempting to copy {image_path} -> {dest}")
        copy_attempts = [
            (["pkexec", "cp", image_path, str(dest)], "pkexec"),
            (["sudo", "cp", image_path, str(dest)], "sudo"),
            (["cp", image_path, str(dest)], "direct")
        ]

        copied = False
        last_err = None
        for cmd, kind in copy_attempts:
            try:
                # Use shell=False so user sees polkit or sudo prompt in GUI/terminal as usual
                subprocess.run(cmd, check=True)
                self.log_msg(f"Copied with {kind}.")
                copied = True
                break
            except FileNotFoundError as e:
                last_err = e
                self.log_msg(f"{kind} not available: {e}")
                continue
            except subprocess.CalledProcessError as e:
                last_err = e
                self.log_msg(f"{kind} failed: {e}")
                continue

        if not copied:
            QtWidgets.QMessageBox.critical(
                self, "Copy failed",
                "Failed to copy wallpaper to login destination. Try running this application as root or install polkit."
            )
            self.log_msg(f"Login copy failed: {last_err}")
            return

        # Try to chown/chmod via sudo (best effort)
        try:
            subprocess.run(["sudo", "chown", "root:root", str(dest)], check=True)
            subprocess.run(["sudo", "chmod", "0644", str(dest)], check=True)
            self.log_msg("Set ownership to root:root and mode 644 on destination.")
        except Exception as e:
            # warn but continue
            self.log_msg(f"Warning: couldn't chown/chmod via sudo: {e}")

        # Success dialog + ask about restart
        QtWidgets.QMessageBox.information(self, "Success", f"Login wallpaper copied to {dest}")
        self.log_msg(f"Login wallpaper copied to {dest}")

        # Ask whether to restart sddm (explicit, warns user)
        reply = QtWidgets.QMessageBox.question(
            self,
            "Restart SDDM?",
            "Restarting SDDM will log out your session. Do you want to restart SDDM now?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                # use sudo to restart (polkit actions may vary)
                subprocess.run(["sudo", "systemctl", "restart", "sddm"], check=True)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Restart failed", f"Failed to restart sddm: {e}")
                self.log_msg(f"Failed to restart sddm: {e}")
            # if restart succeeded, session will end; nothing else to do

    # ------------------- Theme handlers ------------------------------------

    def on_apply_theme(self):
        sel = self.theme_list.currentItem()
        if not sel:
            QtWidgets.QMessageBox.warning(self, "No theme", "Please select a theme.")
            return
        name = sel.text()
        if name == "Choose According to the wallpaper":
            try:
                self._set_qtile_theme_value("cp.wall_color")
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
                self._set_qtile_theme_value(mapping)
                self.log_msg(f"Applied theme: {name} -> {mapping}")
            except Exception as e:
                self.log_msg(f"Theme apply error: {e}")

    def on_apply_choose_wallpaper_theme(self):
        try:
            self._set_qtile_theme_value("cp.wall_color")
            if COLOR_CHANGER_SH.exists():
                run_shell(f"source \"{COLOR_CHANGER_SH}\"", shell=True)
            if TRAYER_PY.exists():
                run_shell(f'"{TRAYER_PY}"', shell=True)
            self.log_msg("Applied cp.wall_color theme and ran color_changer/trayer.")
        except Exception as e:
            self.log_msg(f"Error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def _set_qtile_theme_value(self, value: str):
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

    # ------------------- radio toggle (show/hide position chooser & swatches) -

    def on_action_toggled(self, _=None):
        lock_selected = self.radio_lock.isChecked()
        # Toggle the visibility of the entire position container widget
        self.pos_container.setVisible(lock_selected)

# --------------------------- Entry point -------------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Set a global font if available
    try:
        app.setFont(QtGui.QFont(FONT_FAMILY, FONT_SIZE))
    except Exception:
        pass

    # Apply dark stylesheet
    try:
        app.setStyleSheet(DARK_STYLESHEET)
    except Exception:
        pass

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()