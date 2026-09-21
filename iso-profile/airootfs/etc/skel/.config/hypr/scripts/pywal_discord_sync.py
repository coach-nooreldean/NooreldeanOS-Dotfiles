#!/usr/bin/env python3
import json
import os
import sys

wal_file = os.path.expanduser("~/.cache/wal/colors.json")

if not os.path.exists(wal_file):
    sys.exit(0)

with open(wal_file, "r") as f:
    data = json.load(f)

bg = data["special"]["background"]
fg = data["special"]["foreground"]
colors = data["colors"]

css_content = f"""/**
 * @name Pywal Dynamic Theme
 * @author AntiGravity
 * @description Automatically generated theme based on pywal colors.
 * @version 1.0.0
 */

:root {{
    --background-primary: {bg};
    --background-secondary: {colors["color0"]};
    --background-secondary-alt: {colors["color0"]};
    --background-tertiary: {colors["color0"]};
    --background-accent: {colors["color4"]};
    --background-floating: {bg};
    --text-normal: {fg};
    --text-muted: {colors["color8"]};
    --text-link: {colors["color4"]};
    --brand-experiment: {colors["color4"]};
    --brand-experiment-hover: {colors["color5"]};
    --header-primary: {fg};
    --header-secondary: {colors["color7"]};
    --interactive-normal: {colors["color7"]};
    --interactive-hover: {fg};
    --interactive-active: {fg};
    --interactive-muted: {colors["color8"]};
    --channeltextarea-background: {colors["color0"]};
    --scrollbar-auto-thumb: {colors["color4"]};
    --scrollbar-auto-track: {bg};
    --scrollbar-thin-thumb: {colors["color4"]};
    --scrollbar-thin-track: {bg};
    
    /* Frosted glass effect for Vesktop/Webcord if transparency enabled */
    --background-primary: color-mix(in srgb, {bg} 60%, transparent);
    --background-secondary: color-mix(in srgb, {colors["color0"]} 50%, transparent);
    --background-tertiary: color-mix(in srgb, {colors["color0"]} 50%, transparent);
}}
"""

paths = [
    "~/.config/BetterDiscord/themes",
    "~/.config/vesktop/themes",
    "~/.config/webcord/Themes",
    "~/.config/Vencord/themes",
]

for path in paths:
    full_path = os.path.expanduser(path)
    if not os.path.exists(full_path):
        try:
            os.makedirs(full_path, exist_ok=True)
        except:
            continue
    
    theme_file = os.path.join(full_path, "pywal.theme.css")
    try:
        with open(theme_file, "w") as f:
            f.write(css_content)
    except Exception as e:
        pass
