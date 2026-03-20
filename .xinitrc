#!/bin/sh

~/.fehbg &
xset s off -dpms
exec qtile start

volctl &


