#!/usr/bin/env python3
import json
import os
import sys

wal_file = os.path.expanduser("~/.cache/wal/colors.json")

def hex_to_rgba(hex_str, alpha="ff"):
    hex_str = hex_str.strip("#")
    return f"rgba({hex_str}{alpha})"

if not os.path.exists(wal_file):
    # Provide default fallback colors if pywal hasn't run yet
    colors = {
        "background": "rgba(111111cc)",
        "foreground": "rgba(eeeeeeff)",
        "color0": "rgba(222222ff)",
        "color1": "rgba(ff0000ff)",
        "color2": "rgba(00ff00ff)",
        "color3": "rgba(ffff00ff)",
        "color4": "rgba(0000ffff)",
        "color5": "rgba(ff00ffff)",
        "color6": "rgba(00ffffff)",
        "color7": "rgba(eeeeeeff)",
    }
else:
    with open(wal_file, "r") as f:
        data = json.load(f)

    colors = {
        "background": hex_to_rgba(data["special"]["background"], "cc"),
        "foreground": hex_to_rgba(data["special"]["foreground"], "ff"),
        "color0": hex_to_rgba(data["colors"]["color0"], "ff"),
        "color1": hex_to_rgba(data["colors"]["color1"], "ff"),
        "color2": hex_to_rgba(data["colors"]["color2"], "ff"),
        "color3": hex_to_rgba(data["colors"]["color3"], "ff"),
        "color4": hex_to_rgba(data["colors"]["color4"], "ff"),
        "color5": hex_to_rgba(data["colors"]["color5"], "ff"),
        "color6": hex_to_rgba(data["colors"]["color6"], "ff"),
        "color7": hex_to_rgba(data["colors"]["color7"], "ff"),
    }

conf_content = ""
for k, v in colors.items():
    conf_content += f"${k} = {v}\n"

out_dir = os.path.expanduser("~/.config/hypr")
os.makedirs(out_dir, exist_ok=True)

with open(os.path.join(out_dir, "colors.conf"), "w") as f:
    f.write(conf_content)
