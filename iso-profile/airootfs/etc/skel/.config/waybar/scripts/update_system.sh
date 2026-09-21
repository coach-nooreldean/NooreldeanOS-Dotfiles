#!/bin/bash
echo -e "\033[1;36mStarting System Update...\033[0m"

echo -e "\n\033[1;34m>>> Updating Arch Repositories & AUR (yay)...\033[0m"
yay -Syu

if command -v flatpak &> /dev/null; then
    echo -e "\n\033[1;34m>>> Updating Flatpaks...\033[0m"
    flatpak update -y
fi

if command -v snap &> /dev/null; then
    echo -e "\n\033[1;34m>>> Updating Snaps...\033[0m"
    sudo snap refresh
fi

if command -v fwupdmgr &> /dev/null; then
    echo -e "\n\033[1;34m>>> Checking Firmware Updates...\033[0m"
    fwupdmgr refresh
    fwupdmgr update
fi

# Refresh waybar updates count
pkill -RTMIN+8 waybar

echo -e "\n\033[1;32mSystem Update Complete!\033[0m"
echo "Press Enter to close this window..."
read
