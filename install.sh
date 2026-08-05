#!/bin/bash

# NooreldeanOS Dotfiles Installer
# This script will install packages and set up symlinks for your dotfiles.

set -e

DOTFILES_DIR="$HOME/NooreldeanOS-Dotfiles"

echo -e "\033[1;36mStarting NooreldeanOS Dotfiles Installation...\033[0m"

# 1. System Update & Prerequisites
echo -e "\n\033[1;33m>>> Updating system and installing base prerequisites...\033[0m"
sudo pacman -Syu --noconfirm
sudo pacman -S --needed --noconfirm base-devel git flatpak curl wget

# 2. Install AUR Helper (yay)
if ! command -v yay &> /dev/null; then
    echo -e "\n\033[1;33m>>> Installing yay (AUR Helper)...\033[0m"
    cd /tmp
    git clone https://aur.archlinux.org/yay.git
    cd yay
    makepkg -si --noconfirm
    cd "$DOTFILES_DIR"
else
    echo -e "\n\033[1;32m>>> yay is already installed.\033[0m"
fi

# 3. Install Packages
echo -e "\n\033[1;33m>>> Installing pacman/AUR packages...\033[0m"
if [ -f "$DOTFILES_DIR/pacman-packages.txt" ]; then
    yay -S --needed --noconfirm - - < "$DOTFILES_DIR/pacman-packages.txt"
else
    echo "pacman-packages.txt not found!"
fi

# 4. Install Flatpaks
echo -e "\n\033[1;33m>>> Installing Flatpak packages...\033[0m"
if [ -f "$DOTFILES_DIR/flatpak-packages.txt" ]; then
    xargs -a "$DOTFILES_DIR/flatpak-packages.txt" flatpak install -y flathub
else
    echo "flatpak-packages.txt not found!"
fi

# 5. Setup Configs (Symlinks)
echo -e "\n\033[1;33m>>> Creating symlinks for .config directories...\033[0m"
mkdir -p "$HOME/.config"
for dir in "$DOTFILES_DIR/.config/"*; do
    if [ -d "$dir" ]; then
        dirname=$(basename "$dir")
        # Remove existing config if it's a directory or file (not a symlink) to avoid conflicts
        if [ -e "$HOME/.config/$dirname" ] && [ ! -L "$HOME/.config/$dirname" ]; then
            echo "Backing up existing $HOME/.config/$dirname to $HOME/.config/${dirname}.bak"
            mv "$HOME/.config/$dirname" "$HOME/.config/${dirname}.bak"
        fi
        ln -sfn "$dir" "$HOME/.config/$dirname"
        echo "Symlinked $dirname to ~/.config/"
    fi
done

# 6. Setup Applications (Desktop entries)
echo -e "\n\033[1;33m>>> Installing custom .desktop files...\033[0m"
mkdir -p "$HOME/.local/share/applications"
for app in "$DOTFILES_DIR/applications/"*.desktop; do
    if [ -f "$app" ]; then
        ln -sfn "$app" "$HOME/.local/share/applications/$(basename "$app")"
        echo "Symlinked $(basename "$app")"
    fi
done

# 7. Make scripts executable
echo -e "\n\033[1;33m>>> Making scripts executable...\033[0m"
find "$DOTFILES_DIR/scripts" -type f -name "*.sh" -exec chmod +x {} \;
if [ -d "$DOTFILES_DIR/.config/waybar/scripts" ]; then
    find "$DOTFILES_DIR/.config/waybar/scripts" -type f -name "*.sh" -exec chmod +x {} \;
fi

echo -e "\n\033[1;32mInstallation Complete! Please restart your session/Hyprland to apply changes.\033[0m"
