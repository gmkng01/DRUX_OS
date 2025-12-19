import os
from func_var import bk, bk2, fr, fr2
from subprocess import Popen
from MyBars import mybar, mygroup
from libqtile import layout, hook
from libqtile.config import Match
from libqtile.layout import Floating
from keybindings import mykeys, mymouse
# import os
import subprocess

screens =   mybar
keys =      mykeys
my_mouse =  mymouse
groups =    mygroup

layouts = [
    layout.Bsp(
       border_width = 0,
      #  border_normal = f"#66{bk2[1::]}",
       fullscreen_border_width = 0,
       max_border_width = 0,
       margin =  [7,7,7,7],
    ),
    layout.Max(
       border_width = 0,
    #    border_focus = f"#00{fr2[1::]}"
    #    border_focus = "#ffffff",
       fullscreen_border_width = 0,
       max_border_width = 0,
       margin =  [7,7,7,7],
    ),
    layout.Floating(        
       border_width = 0,
       fullscreen_border_width = 0,
       max_border_width = 0,
       margin =  [0, 0, 0, 0],
    )
]

floating_layout = Floating(
    float_rules=[
         *Floating.default_float_rules,
         Match(wm_class='blueman-manager'),        # Blueman bluetooth manager
         Match(wm_class='pavucontrol'),            # Pavucontrol
         Match(wm_class='kdeconnect-app'),         # Conectivity to the Smartphone
         Match(wm_class='mpv'),                    # MPV video player
         Match(wm_class='vlc'),                    # VLC video player  
         # Match(wm_class='terminator'),             # Terminator  
         Match(wm_class='qbittorrent'),            # QbitTorrent
         Match(wm_class='nm-connection-editor'),   # Network Manager GUI
         Match(wm_class='UI.py'),   # Theme changer

    ]
)

layouts.append(floating_layout)

dgroups_key_binder = None
dgroups_app_rules = []  
follow_mouse_focus = False
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# # Wayland-specific small bits (put near top of config.py)
# from libqtile.backend.wayland.inputs import InputConfig

# # Example: set tap-to-click for a particular touchpad id (use your device id/name)
# wl_input_rules = {
#     "1234:abcd:Touchpad Model": InputConfig(touch=True, 
#                                             tap=True,
#                                             natural_scroll=False,
#                                             pointer_accel=0.3,),
# }

# # You can also use device matching on vendor/product ids or names.


wmname = "LG3D"


# import subprocess


# @hook.subscribe.startup_once


subprocess.run([
    "systemctl", "--user", "import-environment",
    "DISPLAY", "XAUTHORITY"
])

subprocess.run([
    "systemctl", "--user", "start", "graphical-session.target"
])



# @hook.subscribe.startup_once
# def autostart():
#    home = os.path.expanduser('~')
#    Popen([home + '/.config/qtile/scripts/autostart.sh'])
   #  tr = f'trayer --transparent true --width 4 --edge top --align right --alpha 0 --tint 0x{bk[1::]} --margin 0 --distance 0 --distancefrom top'    
   # tr = f"{home}/.config/qtile/trayer.py"
   # Popen(tr, shell=True)
   # Popen([home + '/.config/qtile/scripts/battery_low.sh'])
   # Popen('volctl')


