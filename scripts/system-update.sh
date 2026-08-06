#!/bin/bash
echo -e "\033[1;36mStarting System Update...\033[0m"

echo -e "\n\033[1;33m>>> 1. Updating system packages (pacman + AUR)...\033[0m"
yay -Syu

echo -e "\n\033[1;33m>>> 2. Updating Flatpak apps...\033[0m"
if command -v flatpak &> /dev/null; then
    flatpak update -y
else
    echo "Flatpak not installed, skipping."
fi

echo -e "\n\033[1;32mSystem Update Complete!\033[0m"
read -p "Press Enter to close this window..."
