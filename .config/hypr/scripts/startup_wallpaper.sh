#!/bin/bash
# Wait for the Wayland environment and awww-daemon to settle
sleep 1.5

# Check if this is the very first time the system is booting
if [ ! -f ~/.cache/.wallpaper_initialized ]; then
    # First boot: Set the default Pastel-Window wallpaper
    ~/.config/hypr/scripts/set_wallpaper.sh ~/wallpapers/Pastel-Window.png
    # Mark initialization as done so it never runs again
    mkdir -p ~/.cache
    touch ~/.cache/.wallpaper_initialized
else
    # Not first boot: Just restore whatever the user chose last
    awww restore
fi
