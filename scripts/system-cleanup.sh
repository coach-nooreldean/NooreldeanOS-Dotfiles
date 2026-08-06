#!/bin/bash
echo -e "\033[1;36mStarting System Cleanup...\033[0m"

echo -e "\n\033[1;33m>>> 1. Checking for unused dependencies (Orphans)...\033[0m"
ORPHANS=$(pacman -Qtdq)
if [ -n "$ORPHANS" ]; then
    echo "Found unused packages. You will be prompted to remove them:"
    sudo pacman -Rns "$ORPHANS"
else
    echo "No unused dependencies found."
fi

echo -e "\n\033[1;33m>>> 2. Cleaning Flatpak unused runtimes & apps...\033[0m"
if command -v flatpak &> /dev/null; then
    flatpak uninstall --unused
else
    echo "Flatpak not installed."
fi

echo -e "\n\033[1;33m>>> 3. Cleaning pacman/yay cache...\033[0m"
yay -Sc

echo -e "\n\033[1;33m>>> 4. Cleaning user cache directory (Thumbnails & Yay build files)...\033[0m"
rm -rf ~/.cache/thumbnails/*
rm -rf ~/.cache/yay/*

echo -e "\n\033[1;32mSystem Cleanup Complete!\033[0m"
read -p "Press Enter to close this window..."
