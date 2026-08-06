#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -eo pipefail

# Ensure we are in the directory of the script using absolute path
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DOTFILES_DIR"

echo "🗑️  Uninstalling NooreldeanOS..."

echo "[1] Restoring previous configuration..."
# Find backup directories
mapfile -t BACKUP_DIRS < <(ls -d ~/.NooreldeanOS-backup-* 2>/dev/null | sort -r)

if [ ${#BACKUP_DIRS[@]} -eq 0 ]; then
    LATEST_BACKUP=""
elif [ ${#BACKUP_DIRS[@]} -eq 1 ]; then
    LATEST_BACKUP="${BACKUP_DIRS[0]}"
else
    echo "    Multiple backups found:"
    for i in "${!BACKUP_DIRS[@]}"; do
        echo "    $((i+1))) ${BACKUP_DIRS[$i]}"
    done
    read -p "    Select which backup to restore [1-${#BACKUP_DIRS[@]}]: " SEL
    if [[ "$SEL" =~ ^[0-9]+$ ]] && [ "$SEL" -ge 1 ] && [ "$SEL" -le "${#BACKUP_DIRS[@]}" ]; then
        LATEST_BACKUP="${BACKUP_DIRS[$((SEL-1))]}"
    else
        echo "    ❌ Invalid selection. Aborting."
        exit 1
    fi
fi

if [ -n "$LATEST_BACKUP" ] && [ -d "$LATEST_BACKUP" ]; then
    echo "    Found backup at: $LATEST_BACKUP"
    echo "    Restoring your original configurations..."
    
    # Backup the current (NooreldeanOS) config just in case
    PRE_UNINSTALL_BACKUP=~/.NooreldeanOS-pre-uninstall-backup-$(date +%Y%m%d-%H%M%S)
    mkdir -p "$PRE_UNINSTALL_BACKUP"
    
    # Safely remove NooreldeanOS dotfiles (back them up just in case)
    if [ -d ".config" ]; then
        mkdir -p "$PRE_UNINSTALL_BACKUP/.config"
        for item in .config/*; do
            if [ -e "$item" ]; then
                basename=$(basename "$item")
                if [ -e "$HOME/.config/$basename" ]; then
                    mv "$HOME/.config/$basename" "$PRE_UNINSTALL_BACKUP/.config/" 2>/dev/null || true
                fi
            fi
        done
    fi
    
    # Restore .config
    if [ -d "$LATEST_BACKUP/.config" ]; then
        mkdir -p ~/.config
        if command -v rsync &> /dev/null; then
            rsync -a "$LATEST_BACKUP/.config/" ~/.config/ 2>/dev/null || true
        else
            shopt -s dotglob 2>/dev/null || true
            cp -a "$LATEST_BACKUP/.config/"* ~/.config/ 2>/dev/null || true
            shopt -u dotglob 2>/dev/null || true
        fi
    fi
    
    # Restore local-share
    if [ -d "$LATEST_BACKUP/local-share/icons" ]; then
        mkdir -p ~/.local/share/icons
        cp -a "$LATEST_BACKUP/local-share/icons/"* ~/.local/share/icons/ 2>/dev/null || true
    fi
    if [ -d "$LATEST_BACKUP/local-share/applications" ]; then
        mkdir -p ~/.local/share/applications
        cp -a "$LATEST_BACKUP/local-share/applications/"* ~/.local/share/applications/ 2>/dev/null || true
    fi
    
    # Restore home
    if [ -d "$LATEST_BACKUP/home" ]; then
        cp -a "$LATEST_BACKUP/home/"* ~/ 2>/dev/null || true
    fi

    echo "    ✅ Configurations restored successfully."
else
    echo "    ⚠️  No backup directory found (~/.NooreldeanOS-backup-*). Skipping configuration restore."
fi

echo "[2] Restoring scripts..."
if [ -n "$LATEST_BACKUP" ] && [ -d "$LATEST_BACKUP/home/scripts" ]; then
    cp -a "$LATEST_BACKUP/home/scripts" ~/ 2>/dev/null || true
    echo "    ✅ Scripts restored."
else
    # Removing the specific scripts we added to ~/scripts if no backup
    rm -f ~/scripts/system-update.sh
    rm -f ~/scripts/system-cleanup.sh
    echo "    ✅ Scripts removed."
fi

echo "[3] Cleaning up system configs & services..."
if [ -f /etc/systemd/zram-generator.conf ]; then
    echo "    Removing NooreldeanOS ZRAM configuration..."
    sudo rm -f /etc/systemd/zram-generator.conf 2>/dev/null || true
fi
echo "    Note: Background services (sddm, bluetooth, docker, ufw) are preserved to keep your system functional."
echo "    If you wish to disable any manually, use: sudo systemctl disable <service_name>"

echo "[4] Packages and Apps..."
echo "    ⚠️  WARNING: Removing packages might break your system if other software depends on them!"
echo "    ⚠️  It is highly recommended to leave the packages installed unless you are absolutely sure."
read -p "    ❓ Are you ABSOLUTELY SURE you want to uninstall the packages? [y/N]: " UNINSTALL_PKGS
if [[ "$UNINSTALL_PKGS" =~ ^[Yy]$ ]]; then
    if [ -f pacman-packages.txt ] && [ -s pacman-packages.txt ]; then
        readarray -t PACMAN_PKGS < <(grep -v '^\s*#' pacman-packages.txt | grep -v '^\s*$' || true)
        if [ "${#PACMAN_PKGS[@]}" -gt 0 ]; then
            echo "    Removing pacman/AUR packages..."
            yay -Rns --noconfirm "${PACMAN_PKGS[@]}" || echo "    ⚠️ Some packages couldn't be removed or are required by other packages."
        fi
    fi
    if [ -f flatpak-packages.txt ] && [ -s flatpak-packages.txt ]; then
        readarray -t FLATPAK_PKGS < <(grep -v '^\s*#' flatpak-packages.txt | grep -v '^\s*$' || true)
        if [ "${#FLATPAK_PKGS[@]}" -gt 0 ]; then
            echo "    Removing flatpak packages..."
            for pkg in "${FLATPAK_PKGS[@]}"; do
                sudo flatpak uninstall -y "$pkg" || echo "    ⚠️ Failed to remove flatpak $pkg"
            done
        fi
    fi
else
    echo "    Skipping package removal. If you change your mind, review the 'pacman-packages.txt' and 'flatpak-packages.txt' files and uninstall them manually."
fi
echo ""
rm -f ~/.NooreldeanOS-installed
echo "✅ Uninstallation Complete!"
echo "🔄 Please reboot or log out and log back in to see the changes."
