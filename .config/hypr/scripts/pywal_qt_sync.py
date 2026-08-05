#!/usr/bin/env python3
import json
import os
import sys

wal_file = os.path.expanduser("~/.cache/wal/colors.json")

if not os.path.exists(wal_file):
    sys.exit(0)

with open(wal_file, "r") as f:
    data = json.load(f)

colors = data["colors"]
bg = data["special"]["background"]
fg = data["special"]["foreground"]

c0 = colors["color0"]
c1 = colors["color1"]
c2 = colors["color2"]
c3 = colors["color3"]
c4 = colors["color4"]
c8 = colors["color8"]

# Map roles: WindowText, Button, Light, Midlight, Dark, Mid, Text, BrightText, ButtonText, Base, Window, Shadow, Highlight, HighlightedText, Link, LinkVisited, AlternateBase, DefaultBase, ToolTipBase, ToolTipText, PlaceholderText

palette = f"{fg}, {bg}, {c4}, {c4}, {c0}, {c0}, {fg}, {fg}, {fg}, {c0}, {bg}, {c0}, {c4}, {bg}, {c1}, {c2}, {c0}, {bg}, {bg}, {fg}, {c8}"

ini = f"""[ColorScheme]
active_colors={palette}
inactive_colors={palette}
disabled_colors={palette}
"""

for ver in ["qt5ct", "qt6ct"]:
    out_dir = os.path.expanduser(f"~/.config/{ver}/colors")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "pywal.conf"), "w") as f:
        f.write(ini)

# Set qt5ct to use it
import configparser
for ver in ["qt5ct", "qt6ct"]:
    conf_file = os.path.expanduser(f"~/.config/{ver}/{ver}.conf")
    if os.path.exists(conf_file):
        config = configparser.ConfigParser()
        config.read(conf_file)
        if "Appearance" not in config:
            config["Appearance"] = {}
        config["Appearance"]["color_scheme_path"] = f"~/.config/{ver}/colors/pywal.conf"
        config["Appearance"]["custom_palette"] = "true"
        with open(conf_file, "w") as f:
            config.write(f)

# Reload UI Components to apply new pywal colors instantly
os.system("swaync-client -rs") # reload swaync css
os.system("killall -SIGUSR2 waybar") # reload waybar css
