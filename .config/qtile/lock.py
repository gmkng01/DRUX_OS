#!/usr/bin/env python3

import subprocess
import func_var
# import os
# import colorsys
# import re
from colorthief import ColorThief


# Image path
image_path = "/home/abhi/Pictures/walls/2024-Subaru-WRX-Project-Midnight-Concept-005-2160.jpg"

c = func_var.co

ct = ColorThief(image_path)
palette = ct.get_palette(color_count=2)

wc = {
    "fr": f"#{palette[0][0]:02X}{palette[0][1]:02X}{palette[0][2]:02X}",
    "fr2": f"#{palette[1][0]:02X}{palette[1][1]:02X}{palette[1][2]:02X}",
}



if func_var.co == func_var.cp.wall_color:
    c = wc
else:
    c = func_var.co
    

fr = c['fr']
fr2 = c['fr2']



# Transparency
alpha = "10"
alpha2 = "66"

# Colors
# fr = "#12232B"
# fr2 = "#317A96"
selection = "#44475a"
green = "#50fa7b"
red = "#ff5555"

# background = "#282a36"
# comment = "#6272a4"
# font = "#DDDDDD"
# yellow = "#f1fa8c"
# orange = "#ffb86c"
# magenta = "#ff79c6"
# blue = "#6272a4"
# cyan = "#8be9fd"
  # kept as-is from your script



# Build command
cmd = [
    "i3lock",
    f"--insidever-color={selection}{alpha}",
    f"--insidewrong-color={selection}{alpha}",
    f"--inside-color={selection}{alpha}",
    # f"--ringver-color={green}{alpha}",
    f"--ringwrong-color={red}{alpha}",
    # f"--ring-color={blue}{alpha}",
    "--line-uses-ring",
    # f"--keyhl-color={magenta}{alpha}",
    # f"--bshl-color={orange}{alpha}",
    f"--separator-color={selection}{alpha}",
    f"--verif-color={green}",
    f"--wrong-color={red}",
    f"--modif-color={red}",
    # f"--layout-color={blue}",
    f"--date-color={fr}",
    f"--time-color={fr2}",
    "--screen=1",
    "--force-clock",
    "--indicator",
    "--time-str=%H :%M",
    "--date-str=%a %e %b %Y",
    "--verif-text=Checking...",
    "--wrong-text=Wrong pswd",
    "--noinput=No Input",
    "--lock-text=Locking...",
    "--lockfailed=Lock Failed",
    f"--image={image_path}",
    "--fill",
    "--time-font=NFS Font",
    "--date-font=NFS Font",
    "--layout-font=NFS Font",
    "--verif-font=NFS Font",
    "--wrong-font=NFS Font",
    "--time-align=1",
    "--date-align=1",
    "--date-size=60",
    "--time-size=175",
    "--time-pos=110:550",
    "--date-pos=100:600",
    "--ind-pos=950:942",
    "--bar-pos=-10:860",
    "--bar-base-width=10",
    "--bar-total-width=10",
    "--bar-max-height=30",
    "--bar-indicator",
    "--bar-step=2000",
    "--refresh-rate=1",
    "--bar-count=20000",
]

# Execute
subprocess.run(cmd, check=True)
