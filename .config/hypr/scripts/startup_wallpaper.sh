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
    # Check if the last wallpaper actually exists (e.g. not on an unmounted drive)
    if [ -f ~/.cache/wal/colors.json ]; then
        LAST_WP=$(jq -r .wallpaper ~/.cache/wal/colors.json 2>/dev/null)
        if [ ! -f "$LAST_WP" ]; then
            echo "Last wallpaper $LAST_WP not found. Falling back to default."
            ~/.config/hypr/scripts/set_wallpaper.sh ~/wallpapers/Pastel-Window.png
            exit 0
        fi
    fi
    awww restore
    wal -R -n -e 2>/dev/null || true
fi
