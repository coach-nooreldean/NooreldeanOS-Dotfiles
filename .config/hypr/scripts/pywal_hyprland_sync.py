#!/usr/bin/env python3
import json
import os
import sys

wal_file = os.path.expanduser("~/.cache/wal/colors.json")

if not os.path.exists(wal_file):
    sys.exit(0)

with open(wal_file, "r") as f:
    data = json.load(f)

def hex_to_rgba(hex_str, alpha="ff"):
    hex_str = hex_str.strip("#")
    return f"rgba({hex_str}{alpha})"

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

lua_content = "return {\n"
for k, v in colors.items():
    lua_content += f'    {k} = "{v}",\n'
lua_content += "}\n"

with open(os.path.expanduser("~/.config/hypr/colors.lua"), "w") as f:
    f.write(lua_content)
