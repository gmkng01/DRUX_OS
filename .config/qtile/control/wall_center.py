#!/usr/bin/env python3
"""
qtile_style_center_optimized_with_caching.py

- Implements **Thumbnail Caching** for near-instant gallery loading after the first run.
- Uses a hidden folder (.wall_thumbs) inside the wallpaper directory for cache storage.
- Checks if the cache thumbnail is older than the source image to ensure freshness.

[... existing code comments ...]
"""

import sys
sys.path.append("/home/abhi/.config/qtile")

import os
import re
# import themes.colors
import themes.Color_picker as cp
import shutil
import subprocess

import tempfile
import time
from pathlib import Path
from typing import List

import func_var

from PyQt6 import QtCore, QtGui, QtWidgets

# from func_var import bk, fr, bk2, fr2, gr, trn

# ------------------------ Config (edit if needed) ------------------------
HOME = Path.home()
DEFAULT_WALL_DIR = HOME / "Pictures" / "walls"
NITROGEN_CFG_PATH = HOME / ".config" / "nitrogen" / "bg-saved.cfg"
LOCK_SCRIPT_PATH = HOME / ".config" / "i3lock" / "lock.sh"
LOGIN_IMAGE_DEST = Path("/usr/share/pixmaps/background.jpeg")
QTILE_FUNC_VAR = HOME / ".config" / "qtile" / "func_var.py"
# TRAYER_PY = HOME / ".config" / "qtile" / "trayer.py"
COLOR_CHANGER_SH = Path.cwd() / "color_changer.sh"
THUMB_SIZE = 158
BATCH_SIZE = 12     # thumbnails per batch
THUMB_CACHE_DIR_NAME = ".wall_thumbs" # Hidden folder for cache


# UI appearance
FONT_FAMILY = "JetBrainsMono Nerd Font"   
FONT_SIZE = 12

co = func_var.co
# fix = colors.changable

bk = co['bk']
fr = co['fr']
bk2 = co['bk2']
fr2 = co['fr2']
gr = co['gr']

DARK_STYLESHEET = """
/* --- Minimal Dark Palette (Mapped to QTile variables) --- */

/* Base window and general settings */
QWidget {
    background-color: %BK%; 
    color: %FR%;
    font-family: "%FONT%";
    font-size: %FONTSIZE%pt;
}

/* Preview area and general text */
QLabel {
    color: %FR%;
}

/* List widgets (thumbnails) and selection */
QListWidget {
    background-color: %BK%; /* Dark surface for lists */
    # border: 1px solid %BK2%;
    selection-background-color: %FR2%; /* Clean blue highlight */
    selection-color: #FFFFFF;
}

/* Buttons */
QPushButton {
    background-color: %BK%; 
    color: %FR%;
    border: 1px solid %GR%;
    padding: 6px 10px;
    border-radius: 1px;
}
QPushButton:hover { background-color: %FR2%; } /* Use highlight color on hover */
QPushButton:pressed { background-color: %BK2%; }

# /* Group boxes */
# QGroupBox {
    # border: 1px solid %GR%;
#     margin-top: 6px;
# }


/* Group boxes */
QGroupBox {
    # border: 1px solid %GR%;

    background-color: %BK%; 
    /* Increase margin-top to reserve more space for the title text when the font size is large. 
       We increase 6px to 14px to give more breathing room. */
    margin-top: 14px; 
}

/* IMPORTANT: Style the QGroupBox title (sub-control) explicitly to position it */
QGroupBox::title {
    /* Move the title down into the reserved space */
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px; /* Add slight horizontal padding */
}



/* TextEdit (Log area) / QLineEdit (Dir) */
QTextEdit, QLineEdit, QComboBox {
    background-color: %BK2%;
    # border: 1px solid %GR%;
    color: %FR%;
    padding: 4px;
}

/* Scrollbar */
QScrollBar:vertical {
    background: %BK%;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: %GR%;
    min-height: 20px;
}

/* Frames used as swatches */
# QFrame {
#     border: 1px solid %GR%;
#     background: %BK%;
#     border-radius: 2px;
# }
""".replace("%FONT%", FONT_FAMILY).replace("%FONTSIZE%", str(FONT_SIZE)) \
   .replace("%BK%", bk).replace("%FR%", fr).replace("%BK2%", bk2) \
   .replace("%FR2%", fr2).replace("%GR%", gr)
# -----------------------------------------------------------------------

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp"}


def run_shell(cmd, check=False, shell=False):
    if shell:
        return subprocess.run(cmd, shell=True, check=check)
    else:
        return subprocess.run(cmd, check=check)

# def systemd_restart(service: str):
#     subprocess.run(
#         ["killall", "trayer", "&", "sleep", "1", "&", "systemctl", "--user", "start", service],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL,
#     )

# --------------------------- CACHING UTILITIES -----------------------------

def get_thumb_cache_path(image_path: Path, cache_dir: Path) -> Path:
    """Generates the path for the cached thumbnail."""
    # Use hash or safe filename based on original path for uniqueness
    # Using a simple filename change: 'image.jpg' -> 'image.thumb.png'
    # NOTE: The thumbnail is always saved as PNG to preserve transparency if needed
    
    # We use a path structure inside the cache directory to avoid issues if multiple
    # wallpapers have the same name but are in different folders.
    # We will use a basic hash of the full path for a short, unique name.
    
    import hashlib
    thumb_name = hashlib.sha1(str(image_path).encode('utf-8')).hexdigest() + '.png'
    return cache_dir / thumb_name


# --------------------------- Safe lock updater -----------------------------
# ... (ALL lock script functions remain UNCHANGED) ...
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
    # ... (content remains UNCHANGED) ...
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

# --------------------------- GUI (fast gallery with cache) -----------------------------

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qtile Theme & Wallpaper Center")
        self.resize(1200, 800)
        self.image_path = None
        self._files_to_load: List[Path] = []
        self._load_index = 0
        
        # New: Initialize cache directory path
        self.thumb_cache_dir = DEFAULT_WALL_DIR / THUMB_CACHE_DIR_NAME

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
        self.preview_label.setMinimumSize(300, 200)
        self.preview_label.setStyleSheet("border: 1px solid #23292d; background-color: #1a2024;")
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
        self.thumb_list.setMinimumHeight(THUMB_SIZE + 20)
        self.thumb_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        # Connect currentItemChanged for both mouse clicks and keyboard navigation
        self.thumb_list.currentItemChanged.connect(self.on_thumbnail_current_changed)
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
        left_v_splitter.addWidget(dir_widget)
        
        # Set initial sizes for the vertical split
        left_v_splitter.setSizes([450, 150, 50]) 

        QtCore.QTimer.singleShot(0, self.on_load_directory)

        self._dir_reload_timer = QtCore.QTimer(self)
        self._dir_reload_timer.setSingleShot(True)
        self._dir_reload_timer.timeout.connect(self.on_load_directory)

        # Update cache directory when the user changes the wallpaper directory
        def handle_dir_change():
            self._dir_reload_timer.start(500)
            dirpath = Path(self.dir_edit.text()).expanduser()
            self.thumb_cache_dir = dirpath / THUMB_CACHE_DIR_NAME

        self.dir_edit.textChanged.connect(handle_dir_change)
        
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
        # apply_wall_choice_btn = QtWidgets.QPushButton("Apply 'Choose Acc. to wallpaper'")
        # apply_wall_choice_btn.clicked.connect(self.on_apply_choose_wallpaper_theme)
        # theme_buttons.addWidget(apply_wall_choice_btn)
        right.addLayout(theme_buttons)
        # --- END THEMES SECTION ---
        
        # Add a spacer here to push the action box down
        # right.addStretch(1) 
        
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

        # lock position chooser
        self.pos_container = QtWidgets.QWidget()
        pos_layout = QtWidgets.QHBoxLayout(self.pos_container)
        pos_layout.setContentsMargins(0, 0, 0, 0)

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

        # radio toggles (connected only once)
        self.radio_desktop.toggled.connect(self.on_action_toggled)
        self.radio_lock.toggled.connect(self.on_action_toggled)
        self.radio_login.toggled.connect(self.on_action_toggled)
        
        # Ensure initial state is correct (Lock position hidden)
        self.on_action_toggled(False)
        
        # Connect the size changed event of the preview label to re-scale the image
        self.preview_label.resizeEvent = self.on_preview_label_resized


    # --- method to handle preview image resizing ---
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
        
    # ------------------- Gallery loading (non-blocking batches with cache) --------------

    def on_load_directory(self):
        dirpath = Path(self.dir_edit.text()).expanduser()
        if not dirpath.exists() or not dirpath.is_dir():
            QtWidgets.QMessageBox.warning(self, "Invalid folder", "Please enter a valid wallpapers folder path.")
            return
        
        # Update cache directory path
        self.thumb_cache_dir = dirpath / THUMB_CACHE_DIR_NAME
        # Ensure cache directory exists
        self.thumb_cache_dir.mkdir(exist_ok=True)
        
        files = [p for p in dirpath.iterdir() if p.suffix.lower() in IMAGE_EXTS and p.is_file()]
        files.sort()
        self._files_to_load = files
        self._load_index = 0
        self.thumb_list.clear()
        QtCore.QTimer.singleShot(0, self._process_thumbnail_batch)

    def _process_thumbnail_batch(self):
        end = min(self._load_index + BATCH_SIZE, len(self._files_to_load))
        
        for i in range(self._load_index, end):
            p = self._files_to_load[i]
            
            # --- CACHING LOGIC ---
            cache_path = get_thumb_cache_path(p, self.thumb_cache_dir)
            pix = QtGui.QPixmap()
            
            # Check cache validity
            if cache_path.exists():
                # Check if source file is newer than cache file (optimization: skip if files are huge)
                try:
                    if p.stat().st_mtime < cache_path.stat().st_mtime:
                        pix.load(str(cache_path))
                except OSError:
                    # File stats failed, force regen
                    pass

            if pix.isNull():
                # Cache miss or invalid, generate new thumbnail
                full_pix = QtGui.QPixmap(str(p))
                if full_pix.isNull():
                    continue

                pix = full_pix.scaled(THUMB_SIZE, THUMB_SIZE,
                                      QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                      QtCore.Qt.TransformationMode.SmoothTransformation)
                
                # Save to cache asynchronously (don't wait for save to finish, but QPixmap.save is blocking)
                # Save quality 90 for JPEG, but we use PNG for consistency/simplicity here.
                pix.save(str(cache_path), "PNG")
            # --- END CACHING LOGIC ---
            
            icon = QtGui.QIcon(pix)
            item = QtWidgets.QListWidgetItem()
            item.setIcon(icon)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, str(p))

            self.thumb_list.addItem(item)
            
        self._load_index = end
        
        if self._load_index < len(self._files_to_load):
            # Reduced delay for smoother load, but still asynchronous
            QtCore.QTimer.singleShot(1, self._process_thumbnail_batch)
        # else:
            # Gallery load complete (No log messages)


    # ------------------- Thumbnail events & preview -------------------------

    def on_thumbnail_current_changed(self, current: QtWidgets.QListWidgetItem, previous: QtWidgets.QListWidgetItem):
        """Loads the image preview when the currently selected item changes (via mouse or keyboard)."""
        if current:
            path = current.data(QtCore.Qt.ItemDataRole.UserRole)
            if path:
                self.load_image_preview(path)
    
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

    # ------------------- Apply logic ----------------------------------------
    
    # ... (ALL apply, theme, and radio toggle methods remain UNCHANGED in content) ...
    # def apply_image_at_path(self, path: str):
    #     try:
    #         if self.radio_desktop.isChecked():
    #             self._apply_desktop(path)
    #         elif self.radio_lock.isChecked():
    #             idx = self.pos_combo.currentIndex()
    #             tpos, dpos = self.pos_combo.itemData(idx) if idx >= 0 else (None, None)
                
    #             fr = "#2C3333"
    #             fr2 = "#444444" 
                
    #             safe_update_lock_script(path, time_pos=tpos, date_pos=dpos, fr=fr, fr2=fr2)
    #         elif self.radio_login.isChecked():
    #             self.set_login_wallpaper(path)
    #     except Exception as e:
    #         QtWidgets.QMessageBox.critical(self, "Error", str(e))




    def apply_image_at_path(self, path: str):
        try:
            if self.radio_desktop.isChecked():
                self._apply_desktop(path)
                
            elif self.radio_lock.isChecked():
                # --- Dynamic Color Extraction Logic ---
                import func_var
                from colorthief import ColorThief
                
                # Default colors from your current config
                current_colors = func_var.co
                
                # Extract colors from the wallpaper
                ct = ColorThief(path)
                palette = ct.get_palette(color_count=2)
                
                # Format extracted colors to Hex
                wc = {
                    "fr": f"#{palette[0][0]:02X}{palette[0][1]:02X}{palette[0][2]:02X}",
                    "fr2": f"#{palette[1][0]:02X}{palette[1][1]:02X}{palette[1][2]:02X}",
                }

                # Determine which colors to use based on your QTile setting
                if func_var.co == func_var.cp.wall_color:
                    chosen_colors = wc
                else:
                    chosen_colors = current_colors
                
                # Get the lock position from the UI
                idx = self.pos_combo.currentIndex()
                tpos, dpos = self.pos_combo.itemData(idx) if idx >= 0 else (None, None)
                
                # Apply the colors to the lock script
                safe_update_lock_script(
                    path, 
                    time_pos=tpos, 
                    date_pos=dpos, 
                    fr=chosen_colors['fr'], 
                    fr2=chosen_colors['fr2']
                )
                
            elif self.radio_login.isChecked():
                self.set_login_wallpaper(path)
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to apply: {str(e)}")

    def on_apply_image(self):
        if not self.image_path:
            QtWidgets.QMessageBox.warning(self, "No image", "Please select an image (from gallery) first.")
            return
        self.apply_image_at_path(self.image_path)

    def _apply_desktop(self, image_path: str):
        p = NITROGEN_CFG_PATH
        if not p.exists():
            raise FileNotFoundError(f"Nitrogen config not found at {p}")
        
        with open(p, "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                if line.startswith("file="):
                    f.write(f"file={image_path}\n")
                else:
                    f.write(line)
            f.truncate()
            
        try:
            run_shell(["nitrogen", "--restore"])
        except Exception:
            pass
        
        # chained = 'qtile cmd-obj -o cmd -f restart && source ./color_changer.sh && sleep 3 && "{}" &'.format(
        #     TRAYER_PY
        # )
        # run_shell(chained, shell=True)
        # run_shell('sleep 1', shell=True)
        # run_shell(f'"{TRAYER_PY}"', shell=True)

        run_shell(["qtile", "cmd-obj", "-o", "cmd", "-f", "restart"])

        if COLOR_CHANGER_SH.exists():
            run_shell(["bash", str(COLOR_CHANGER_SH)])

        run_shell(["systemctl", "--user", "restart", "trayer.service"])
        # systemd_restart("trayer.service")



    def set_login_wallpaper(self, image_path: str, dest: Path = LOGIN_IMAGE_DEST):
        if not Path(image_path).exists():
            QtWidgets.QMessageBox.critical(self, "Error", f"Image not found: {image_path}")
            return

        copy_attempts = [
            (["pkexec", "cp", image_path, str(dest)], "pkexec"),
            (["sudo", "cp", image_path, str(dest)], "sudo"),
            (["cp", image_path, str(dest)], "direct")
        ]

        copied = False
        for cmd, kind in copy_attempts:
            try:
                subprocess.run(cmd, check=True)
                copied = True
                break
            except Exception:
                continue

        if not copied:
            QtWidgets.QMessageBox.critical(
                self, "Copy failed",
                "Failed to copy wallpaper to login destination. Try running this application as root or install polkit."
            )
            return

        try:
            subprocess.run(["sudo", "chown", "root:root", str(dest)], check=True)
            subprocess.run(["sudo", "chmod", "0644", str(dest)], check=True)
        except Exception:
            pass 

        QtWidgets.QMessageBox.information(self, "Success", f"Login wallpaper changed")

        # reply = QtWidgets.QMessageBox.question(
        #     self,
        #     "Restart SDDM?",
        #     "Restarting SDDM will log out your session. Do you want to restart SDDM now?",
        #     QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        # )
        # if reply == QtWidgets.QMessageBox.StandardButton.Yes:
        #     try:
        #         subprocess.run(["sudo", "systemctl", "restart", "lightdm"], check=True)
        #     except Exception as e:
        #         QtWidgets.QMessageBox.critical(self, "Restart failed", f"Failed to restart sddm: {e}")


    def on_apply_theme(self):
        sel = self.theme_list.currentItem()
        if not sel:
            QtWidgets.QMessageBox.warning(self, "No theme", "Please select a theme.")
            return
        name = sel.text()
        if name == "Choose According to the wallpaper":
            try:
                self._set_qtile_theme_value("cp.wall_color")
            except Exception:
                pass
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
            except Exception:
                pass

    def on_apply_choose_wallpaper_theme(self):
        try:
            self._set_qtile_theme_value("cp.wall_color")
            # if COLOR_CHANGER_SH.exists():
            #     run_shell(f"source \"{COLOR_CHANGER_SH}\"", shell=True)
            # if TRAYER_PY.exists():
            #     run_shell(f'"{TRAYER_PY}"', shell=True)


            if COLOR_CHANGER_SH.exists():
                run_shell(["bash", str(COLOR_CHANGER_SH)])

            # systemd_restart("trayer.service")
            run_shell(["systemctl", "--user", "restart", "trayer.service"])
              
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def _set_qtile_theme_value(self, value: str):
        p = QTILE_FUNC_VAR
        if not p.exists():
            raise FileNotFoundError(f"qtile func var not found: {p}")
        
        with open(p, "r+") as f:
            content = f.read()
            f.seek(0)
            content_new = re.sub(r"^co\s*=.*$", f"co = {value}", content, flags=re.MULTILINE)
            f.write(content_new)
            f.truncate()
            
        run_shell(["qtile", "cmd-obj", "-o", "cmd", "-f", "restart"])
        if COLOR_CHANGER_SH.exists():
            run_shell(["bash", str(COLOR_CHANGER_SH)])

        # systemd_restart("trayer.service")
        run_shell(["systemctl", "--user", "restart", "trayer.service"])

    def on_action_toggled(self, _=None):
        lock_selected = self.radio_lock.isChecked()
        self.pos_container.setVisible(lock_selected)


# --------------------------- Entry point -------------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)

    try:
        app.setFont(QtGui.QFont(FONT_FAMILY, FONT_SIZE))
    except Exception:
        pass

    try:
        app.setStyleSheet(DARK_STYLESHEET)
    except Exception:
        pass

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()