#!/usr/bin/env python3

import os
import subprocess
import time
from pathlib import Path

LOG = Path.home() / ".cache" / "qtile-autostart.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

def log(msg: str):
    with open(LOG, "a") as f:
        f.write(msg + "\n")

log(f"==== Qtile autostart: {time.ctime()} ====")

def is_running(process_name: str) -> bool:
    """Check if a process is already running."""
    try:
        subprocess.run(
            ["pgrep", "-x", process_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False

def run(cmd, name=None):
    """
    Run a command if not already running.
    `name` is the process name used for pgrep.
    """
    pname = name or cmd[0]
    if is_running(pname):
        log(f"Already running: {pname}")
        return
    log(f"Starting: {' '.join(cmd)}")
    subprocess.Popen(cmd)

# ------------------- Startup sequence -------------------

# compositor
run(["picom", "--no-fading-openclose"], "picom")

# wallpaper
subprocess.Popen(["nitrogen", "--restore"])

# polkit agent
run(
    ["/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1"],
    "polkit-gnome-authentication-agent-1",
)

# ------------------- tray (CRITICAL) -------------------

TRAYER_SCRIPT = Path.home() / ".config" / "qtile" / "trayer.py"

if not is_running("trayer"):
    log("Starting trayer...")
    subprocess.Popen([str(TRAYER_SCRIPT)])

# wait for system tray to actually exist
# log("Waiting for system tray...")
# tray_found = False
# for _ in range(20):  # ~6 seconds max
#     try:
#         subprocess.run(
#             ["xprop", "-root", "_NET_SYSTEM_TRAY_S0"],
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL,
#             check=True,
#         )
#         tray_found = True
#         log("System tray detected")
#         break
#     except subprocess.CalledProcessError:
#         time.sleep(0.3)

# if not tray_found:
#     log("WARNING: System tray not detected")

# ------------------- tray-dependent apps -------------------

run(["nm-applet"], "nm-applet")
run(["blueman-applet"], "blueman-applet")
run(["volctl"], "volctl")

# ------------------- battery notifier -------------------

BATTERY_SCRIPT = Path.home() / ".config" / "scripts" / "battery_low.sh"
if BATTERY_SCRIPT.exists():
    run([str(BATTERY_SCRIPT)], "battery_low.sh")
else:
    log("Battery script not found")

log("Autostart complete")
