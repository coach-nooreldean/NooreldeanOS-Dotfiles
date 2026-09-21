#!/usr/bin/env python3
import os
import json
import math
import subprocess
import configparser

# The base directory where Pywal saves colors
WAL_CACHE = os.path.expanduser("~/.cache/wal/colors.json")
GTK_SETTINGS = os.path.expanduser("~/.config/gtk-3.0/settings.ini")

# Catppuccin Mocha Colors available in the cursor pack
CATPPUCCIN_COLORS = {
    "rosewater": "#f5e0dc",
    "flamingo": "#f2cdcd",
    "pink": "#f5c2e7",
    "mauve": "#cba6f7",
    "red": "#f38ba8",
    "maroon": "#eba0ac",
    "peach": "#fab387",
    "yellow": "#f9e2af",
    "green": "#a6e3a1",
    "teal": "#94e2d5",
    "sky": "#89dceb",
    "sapphire": "#74c7ec",
    "blue": "#89b4fa",
    "lavender": "#b4befe"
}

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)

def get_closest_cursor_color(accent_hex):
    accent_rgb = hex_to_rgb(accent_hex)
    closest_name = None
    min_dist = float('inf')
    
    for name, hex_val in CATPPUCCIN_COLORS.items():
        dist = color_distance(accent_rgb, hex_to_rgb(hex_val))
        if dist < min_dist:
            min_dist = dist
            closest_name = name
            
    return closest_name

def apply_cursor(color_name):
    theme_name = f"catppuccin-mocha-{color_name}-cursors"
    print(f"Applying cursor theme: {theme_name}")
    
    # 1. Apply to Hyprland dynamically
    try:
        subprocess.run(["hyprctl", "setcursor", theme_name, "24"], check=True)
    except Exception as e:
        print(f"Error applying to Hyprland: {e}")
        
    # 2. Persist in GTK Settings
    if os.path.exists(GTK_SETTINGS):
        config = configparser.ConfigParser()
        # GTK settingsini doesn't have headers sometimes, we need to handle that
        # But usually it starts with [Settings]
        config.read(GTK_SETTINGS)
        if "Settings" in config:
            config["Settings"]["gtk-cursor-theme-name"] = theme_name
            with open(GTK_SETTINGS, 'w') as f:
                config.write(f)
                
    # 3. Apply to environment/gsettings if possible (for flatpaks)
    try:
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", theme_name], check=False)
    except Exception:
        pass

def main():
    if not os.path.exists(WAL_CACHE):
        print("Pywal cache not found!")
        return

    with open(WAL_CACHE, 'r') as f:
        data = json.load(f)
        
    # color2 is usually the primary accent color in Pywal
    accent_color = data['colors']['color2']
    
    closest_color = get_closest_cursor_color(accent_color)
    print(f"Pywal Accent: {accent_color} -> Closest Catppuccin: {closest_color}")
    
    apply_cursor(closest_color)

if __name__ == "__main__":
    main()
