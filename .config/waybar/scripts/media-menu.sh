#!/bin/bash

# Get current player status and metadata
status=$(playerctl status 2>/dev/null)
if [ "$status" == "Playing" ]; then
    play_pause=""
else
    play_pause=""
fi

title=$(playerctl metadata --format '{{title}}' 2>/dev/null)
artist=$(playerctl metadata --format '{{artist}}' 2>/dev/null)

if [ -z "$title" ]; then
    prompt="No Media Playing"
else
    if [ -n "$artist" ]; then
        prompt="$title - $artist"
    else
        prompt="$title"
    fi
fi

# Truncate prompt if too long to fit nicely
if [ ${#prompt} -gt 35 ]; then
    prompt="${prompt:0:32}..."
fi

# The four horizontal options
options="󰒮\n$play_pause\n\n󰒭"

chosen=$(echo -e "$options" | rofi -dmenu -i -p "$prompt" -theme ~/.config/rofi/media.rasi)

case "$chosen" in
    "󰒮") playerctl previous ;;
    ""|"") playerctl play-pause ;;
    "") playerctl stop ;;
    "󰒭") playerctl next ;;
esac
