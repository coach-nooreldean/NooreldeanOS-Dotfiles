#!/bin/bash

MODE="${1:-region}"
SAVE_DIR="$HOME/Pictures/Screenshots"
mkdir -p "$SAVE_DIR"
FILENAME="screenshot_$(date +%Y-%m-%d_%H-%M-%S).png"
FILEPATH="$SAVE_DIR/$FILENAME"

hyprctl keyword decoration:inactive_opacity 1.0
hyprctl keyword general:border_size 0
hyprctl keyword decoration:shadow:enabled false
sleep 0.2

if [ "$MODE" = "region" ]; then
    grim -g "$(slurp -w 0 -b 00000044)" "$FILEPATH"
else
    grim "$FILEPATH"
fi

hyprctl keyword decoration:inactive_opacity 0.85
hyprctl keyword general:border_size 4
hyprctl keyword decoration:shadow:enabled true

if [ -f "$FILEPATH" ]; then
    wl-copy < "$FILEPATH"
    notify-send "Screenshot Saved" "Saved to $FILEPATH and copied to clipboard." -i "$FILEPATH"
fi
