#!/usr/bin/env python3

# import os
# import sys
# sys.path.append("/home/abhi/.config/qtile")
# from func_var import bk  # safe to import after env is set

# # HARD guarantee X11 environment
# os.environ.setdefault("DISPLAY", ":0")
# os.environ.setdefault(
#     "XAUTHORITY",
#     os.path.expanduser("~/.Xauthority")
# )



# cmd = [
#     "/usr/bin/trayer",
#             '--transparent', 'true',
#             '--width', '6',
#             '--edge', 'top',
#             '--align', 'right',
#             '--alpha', '0',
#             '--tint', f'0x{bk[1::]}',
#             '--margin', '0',
#             '--distance', '0',
#             '--height', '22',
#             '--distancefrom', 'top'
# ]

# # Replace Python with trayer (CRITICAL)
# os.execv(cmd[0], cmd)



import os
import sys
import subprocess

# HARD STOP if trayer already running
if subprocess.run(["pgrep", "-x", "trayer"],
                  stdout=subprocess.DEVNULL).returncode == 0:
    sys.exit(0)

sys.path.append("/home/abhi/.config/qtile")
from func_var import bk

os.environ.setdefault("DISPLAY", ":0")
os.environ.setdefault("XAUTHORITY", os.path.expanduser("~/.Xauthority"))

cmd = [
    "/usr/bin/trayer",
    "--transparent", "true",
    "--width", "6",
    "--edge", "top",
    "--align", "right",
    "--alpha", "0",
    "--tint", f"0x{bk[1:]}",
    "--margin", "0",
    "--distance", "0",
    "--height", "22",
    "--distancefrom", "top",
]

os.execv(cmd[0], cmd)
