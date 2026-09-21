#!/usr/bin/env python3
import json
import os
import sys
import subprocess

wal_file = os.path.expanduser("~/.cache/wal/colors.json")

if not os.path.exists(wal_file):
    sys.exit(0)

with open(wal_file, "r") as f:
    data = json.load(f)

bg = data["special"]["background"].strip("#")
fg = data["special"]["foreground"].strip("#")
c0 = data["colors"]["color0"].strip("#")
c1 = data["colors"]["color1"].strip("#")
c2 = data["colors"]["color2"].strip("#")
c4 = data["colors"]["color4"].strip("#")
c8 = data["colors"]["color8"].strip("#")

ini = f"""[Pywal]
text               = {fg}
subtext            = {c8}
button-text        = {bg}
main               = {bg}
sidebar            = {bg}
player             = {c0}
card               = {c0}
shadow             = 000000
selected-row       = {c4}
button             = {c4}
button-active      = {c4}
button-disabled    = {c8}
tab-active         = {c4}
notification       = {c4}
notification-error = {c1}
misc               = {c0}
"""

theme_dir = os.path.expanduser("~/.config/spicetify/Themes/Pywal")
os.makedirs(theme_dir, exist_ok=True)
with open(os.path.join(theme_dir, "color.ini"), "w") as f:
    f.write(ini)

with open(os.path.join(theme_dir, "user.css"), "w") as f:
    f.write("/* Pywal Spicetify Theme */\n")

# Apply theme
spicetify_bin = os.path.expanduser("~/.spicetify/spicetify")
if os.path.exists(spicetify_bin):
    subprocess.Popen([spicetify_bin, "config", "current_theme", "Pywal"])
    subprocess.Popen([spicetify_bin, "config", "color_scheme", "Pywal"])
    subprocess.Popen([spicetify_bin, "apply"])
