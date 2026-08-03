#!/usr/bin/env bash

alpha='10'
alpha2='66'
background='#282a36'
selection='#44475a'
comment='#6272a4'
font='#DDDDDD'
fr="#405154"
fr2="#C4C7C5"

yellow='#f1fa8c'
orange='#ffb86c'
red='#ff5555'
magenta='#ff79c6'
blue='#6272a4'
cyan='#8be9fd'
green='50fa7b'
# trn = '#ffffff00'

i3lock \
  --nofork \
  --insidever-color=$selection$alpha \
  --insidewrong-color=$selection$alpha \
  --inside-color=$selection$alpha \
  --ringver-color=$green$alpha \
  --ringwrong-color=$red$alpha \
  --ringver-color=$green$alpha \
  --ringwrong-color=$red$alpha \
  --ring-color=$blue$alpha \
  --line-uses-ring \
  --keyhl-color=$magenta$alpha \
  --bshl-color=$orange$alpha \
  --separator-color=$selection$alpha \
  --verif-color=$green \
  --wrong-color=$red \
  --modif-color=$red \
  --layout-color=$blue \
  --date-color=$fr \
  --time-color=$fr2 \
  --screen 1 \
  --force-clock \
  --indicator \
  --time-str="%H :%M" \
  --date-str="%a %e %b %Y" \
  --verif-text="Checking..." \
  --wrong-text="Wrong pswd" \
  --noinput="No Input" \
  --lock-text="Locking..." \
  --lockfailed="Lock Failed" \
  --image="$HOME/Pictures/walls/hum2cso9o0fh1.png" \
  --fill \
  --time-font="NFS Font" \
  --date-font="NFS Font" \
  --layout-font="NFS Font" \
  --verif-font="NFS Font" \
  --wrong-font="NFS Font" \
  --time-align=1 \
  --date-align=1 \
  --date-size=60 \
  --time-size=175 \
  --time-pos="710:200" \
  --date-pos="700:250" \
  --ind-pos="950:942"\
  --bar-pos="-10:860" \
  --bar-base-width=10 \
  --bar-total-width=10 \
  --bar-max-height=30 \
  --bar-indicator \
  --bar-step=2000 \
  --refresh-rate=1 \
  --bar-count=20000