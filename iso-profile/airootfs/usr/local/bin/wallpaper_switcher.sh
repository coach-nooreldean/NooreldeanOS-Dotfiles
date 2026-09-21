#!/usr/bin/env bash
# ==============================================================================
# Rofi Wallpaper & Theme Switcher - NooreldeanOS
# ==============================================================================

set -eo pipefail

WALLPAPERS_DIR="$HOME/wallpapers"
if [ ! -d "$WALLPAPERS_DIR" ]; then
    WALLPAPERS_DIR="/mnt/data2/documents/githup/NooreldeanOS-Dotfiles/wallpapers"
fi

if [ ! -d "$WALLPAPERS_DIR" ]; then
    notify-send "NooreldeanOS" "مجلد الخلفيات غير موجود!" -u critical
    exit 1
fi

ROFI_THEME="$HOME/.config/rofi/wallpaper.rasi"

# Generate entries with thumbnails for rofi dmenu
generate_entries() {
    find -L "$WALLPAPERS_DIR" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) | sort | while read -r img; do
        filename=$(basename "$img")
        name="${filename%.*}"
        echo -en "${name}\0icon\x1f${img}\n"
    done
}

# Run Rofi and get selection
SELECTED_NAME=$(generate_entries | rofi -dmenu -theme "$ROFI_THEME" -p "🖼️  خلفيات NooreldeanOS")

# If user cancelled or selected nothing
if [ -z "$SELECTED_NAME" ]; then
    exit 0
fi

# Find the full path of the selected wallpaper
SELECTED_FILE=$(find -L "$WALLPAPERS_DIR" -maxdepth 1 -type f \( -name "${SELECTED_NAME}.png" -o -name "${SELECTED_NAME}.jpg" -o -name "${SELECTED_NAME}.jpeg" -o -name "${SELECTED_NAME}.webp" \) | head -n 1)

if [ -n "$SELECTED_FILE" ] && [ -f "$SELECTED_FILE" ]; then
    # Apply wallpaper and Pywal color scheme
    "$HOME/.config/hypr/scripts/set_wallpaper.sh" "$SELECTED_FILE"
    notify-send "NooreldeanOS" "تم تطبيق خلفية (${SELECTED_NAME}) وتحديث الألوان!" -i "$SELECTED_FILE"
else
    notify-send "NooreldeanOS" "تعذر العثور على مسار ملف الخلفية المختار." -u normal
fi
