#!/bin/bash

chosen=$(printf " Lock\n󰒲 Suspend\n󰜉 Reboot\n Shutdown\n Logout" | \
rofi -dmenu -i -p "Power")

case "$chosen" in
    " Lock")
        hyprlock
        ;;
    "󰒲 Suspend")
        systemctl suspend
        ;;
    "󰜉 Reboot")
        systemctl reboot
        ;;
    " Shutdown")
        systemctl poweroff
        ;;
    " Logout")
        hyprctl dispatch exit
        ;;
esac
