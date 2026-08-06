#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -eo pipefail

# Ensure we are in the directory of the script using absolute path
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DOTFILES_DIR"

# Prevent running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ ERROR: Please do not run this script as root! Run it as your normal user."
    exit 1
fi

# Clean up any leftover temp sudoers from a previous interrupted run
sudo rm -f /etc/sudoers.d/99-temp-nopasswd 2>/dev/null || true

# Ask for sudo password upfront
echo "🔑 Please enter your password to grant sudo access for the installation:"
sudo -v
# Keep-alive: update existing sudo time stamp if set, otherwise do nothing.
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &
SUDO_KEEP_ALIVE_PID=$!

# Ensure the keep-alive is killed on exit or interruption
trap 'kill $SUDO_KEEP_ALIVE_PID 2>/dev/null; [ -n "$YAY_TMP" ] && rm -rf "$YAY_TMP" 2>/dev/null' EXIT SIGINT

# Error handler: show which step failed before exiting
trap 'kill $SUDO_KEEP_ALIVE_PID 2>/dev/null; [ -n "$YAY_TMP" ] && rm -rf "$YAY_TMP" 2>/dev/null; echo -e "\n❌ ERROR: Installation failed at step: $CURRENT_STEP (line $LINENO)\n💡 Tip: Check your internet connection or any specific error messages above.\n🔄 You can safely re-run this script after fixing the issue."' ERR
echo "🌐 Checking internet connection..."
ping -c 1 -W 3 1.1.1.1 &> /dev/null || curl -Is --connect-timeout 3 https://archlinux.org &> /dev/null || { echo "❌ Error: No internet connection."; exit 1; }
CURRENT_STEP="Initialization"

# Directory is already set at the top of the script using DOTFILES_DIR
echo "🚀 Installing NooreldeanOS..."
CURRENT_STEP="Installing packages"
echo "[1] Installing all programs (This will take time)..."

# Check and install yay if not present
if ! command -v yay &> /dev/null; then
    echo "📦 'yay' is not installed. Installing yay-bin (Pre-compiled for speed)..."
    sudo pacman -S --needed --noconfirm git base-devel
    YAY_TMP=$(mktemp -d)
    git clone https://aur.archlinux.org/yay-bin.git "$YAY_TMP"
    (cd "$YAY_TMP" && makepkg -si --noconfirm)
    rm -rf "$YAY_TMP"
fi

if [ -f pacman-packages.txt ] && [ -s pacman-packages.txt ]; then
    readarray -t PACMAN_PKGS < <(cat pacman-packages.txt | tr -d '\r' | grep -v '^\s*#' | grep -v '^\s*$' || true)
    if [ "${#PACMAN_PKGS[@]}" -gt 0 ]; then
        echo "📦 Installing packages..."
        if ! yay -S --needed --noconfirm --answerclean All --answerdiff None --answeredit None "${PACMAN_PKGS[@]}"; then
            echo "⚠️ Some packages failed to install together. Attempting to install them one by one..."
            for pkg in "${PACMAN_PKGS[@]}"; do
                yay -S --needed --noconfirm --answerclean All --answerdiff None --answeredit None "$pkg" || echo "❌ Failed to install $pkg, skipping..."
            done
        fi
    fi
fi
if [ -f flatpak-packages.txt ] && [ -s flatpak-packages.txt ]; then
    readarray -t FLATPAK_PKGS < <(cat flatpak-packages.txt | tr -d '\r' | grep -v '^\s*#' | grep -v '^\s*$' || true)
    if [ "${#FLATPAK_PKGS[@]}" -gt 0 ]; then
        if ! command -v flatpak &> /dev/null; then
            echo "📦 'flatpak' is not installed. Installing flatpak..."
            sudo pacman -S --needed --noconfirm flatpak
        fi
        echo "🌐 Enabling Flathub repository..."
        sudo flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true
        echo "    Attempting to install all flatpaks in batch for faster resolution..."
        if ! sudo flatpak install -y --noninteractive flathub "${FLATPAK_PKGS[@]}"; then
            echo "    ⚠️ Batch install failed, falling back to individual installation..."
            for pkg in "${FLATPAK_PKGS[@]}"; do
                sudo flatpak install -y --noninteractive flathub "$pkg" || echo "❌ Failed to install flatpak $pkg, skipping..."
            done
        fi
    fi
fi

CURRENT_STEP="Backing up configurations"
if [ -f ~/.NooreldeanOS-installed ]; then
    echo "[2] Skipping backup because NooreldeanOS is already installed."
else
    echo "[2] Backing up existing configurations..."
    BACKUP_DIR=~/.NooreldeanOS-backup-$(date +%Y%m%d-%H%M%S)
    mkdir -p "$BACKUP_DIR/.config" "$BACKUP_DIR/local-share" "$BACKUP_DIR/home"
    echo "    Backing up specific dotfiles and directories that will be modified..."

    safe_backup() {
        if [ -e "$1" ]; then
            cp -a "$1" "$2" 2>/dev/null || echo "    ⚠️ Warning: Failed to backup $1"
        fi
    }

    # Backup .config subdirectories that we will overwrite
    for item in .config/*; do
        if [ -e "$item" ]; then
            basename=$(basename "$item")
            safe_backup "$HOME/.config/$basename" "$BACKUP_DIR/.config/"
        fi
    done

    # Backup other directories being overwritten
    if [ -d "home/icons" ]; then
        safe_backup "$HOME/.local/share/icons" "$BACKUP_DIR/local-share/"
    fi

    if [ -d "$HOME/scripts" ]; then
        safe_backup "$HOME/scripts" "$BACKUP_DIR/home/"
    fi

    # Backup home dotfiles that will be overwritten
    if [ -d "home" ]; then
        for f in home/.bash*; do
            if [ -e "$f" ]; then
                fname=$(basename "$f")
                safe_backup "$HOME/$fname" "$BACKUP_DIR/home/"
            fi
        done
    fi

    if [ -d "applications" ]; then
        safe_backup "$HOME/.local/share/applications" "$BACKUP_DIR/local-share/"
    fi

    echo "    Backup saved to: $BACKUP_DIR"
fi
CURRENT_STEP="Restoring configurations"
echo "[3] Restoring Configurations..."
mkdir -p ~/.config ~/.local/share/icons ~/.local/share/applications ~/scripts

echo "🔗 Do you want to use Symlinks for your dotfiles?"
echo "   (Choose 'y' if you plan to edit configs and push to Github, choose 'n' for a standard stable install)"
read -p "    Use Symlinks? [y/N]: " USE_SYMLINKS

if [[ "$USE_SYMLINKS" =~ ^[Yy]$ ]]; then
    echo "    Creating Symlinks (Developer Mode)..."
    safe_symlink() {
        local src="$1"
        local dest_dir="$2"
        shopt -s dotglob
        for item in "$src"/*; do
            [ -e "$item" ] || continue
            local target="$dest_dir/$(basename "$item")"
            if [ -d "$target" ] && [ ! -L "$target" ]; then
                rm -rf "$target"
            fi
            ln -sfn "$item" "$dest_dir/" 2>/dev/null || true
        done
        shopt -u dotglob
    }

    [ -d ".config" ] && safe_symlink "$DOTFILES_DIR/.config" ~/.config
    [ -d "home/icons" ] && safe_symlink "$DOTFILES_DIR/home/icons" ~/.local/share/icons
    [ -d "home" ] && safe_symlink "$DOTFILES_DIR/home" ~/
    [ -d "scripts" ] && safe_symlink "$DOTFILES_DIR/scripts" ~/scripts
    [ -d "scripts" ] && chmod +x ~/scripts/*.sh 2>/dev/null || true
    [ -d "wallpapers" ] && safe_symlink "$DOTFILES_DIR/wallpapers" ~/wallpapers
    [ -d "applications" ] && safe_symlink "$DOTFILES_DIR/applications" ~/.local/share/applications
elif command -v rsync &> /dev/null; then
    echo "    Copying files using rsync..."
    [ -d ".config" ] && rsync -a .config/ ~/.config/ 2>/dev/null || true
    [ -d "home/icons" ] && rsync -a home/icons/ ~/.local/share/icons/ 2>/dev/null || true
    [ -d "home" ] && rsync -a home/.bash* ~/ 2>/dev/null || true
    [ -d "scripts" ] && rsync -a scripts/ ~/scripts/ 2>/dev/null || true
    [ -d "scripts" ] && chmod +x ~/scripts/*.sh 2>/dev/null || true
    [ -d "wallpapers" ] && rsync -a wallpapers/ ~/wallpapers/ 2>/dev/null || true
    [ -d "applications" ] && rsync -a applications/ ~/.local/share/applications/ 2>/dev/null || true
else
    # Fallback if rsync is somehow not installed
    echo "    Copying files using cp..."
    shopt -s dotglob
    [ -d ".config" ] && cp -a .config/* ~/.config/ 2>/dev/null || true
    [ -d "home/icons" ] && cp -a home/icons/* ~/.local/share/icons/ 2>/dev/null || true
    [ -d "home" ] && cp -a home/.bash* ~/ 2>/dev/null || true
    [ -d "scripts" ] && cp -a scripts/* ~/scripts/ 2>/dev/null || true
    [ -d "scripts" ] && chmod +x ~/scripts/*.sh 2>/dev/null || true
    [ -d "wallpapers" ] && cp -a wallpapers ~/ 2>/dev/null || true
    [ -d "applications" ] && cp -a applications/* ~/.local/share/applications/ 2>/dev/null || true
    shopt -u dotglob
fi


# Pre-generate Pywal colors from the default wallpaper so Hyprland has valid colors on first boot
echo "    Generating color scheme from default wallpaper..."
DEFAULT_WALLPAPER="$HOME/wallpapers/Pastel-Window.png"
if [ ! -f "$DEFAULT_WALLPAPER" ]; then
    DEFAULT_WALLPAPER=$(find ~/wallpapers -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) 2>/dev/null | head -n 1 || true)
fi
if command -v wal &> /dev/null && [ -n "$DEFAULT_WALLPAPER" ]; then
    wal -i "$DEFAULT_WALLPAPER" -n -e -q 2>/dev/null || true
    if command -v python3 &> /dev/null && [ -f ~/.config/hypr/scripts/pywal_hyprland_sync.py ]; then
        python3 ~/.config/hypr/scripts/pywal_hyprland_sync.py 2>/dev/null || true
    fi
fi

CURRENT_STEP="Restoring system configs"
echo "[4] Restoring System Configs (Needs Sudo)..."
if [ -d system-configs/sddm ]; then
    sudo mkdir -p /etc/sddm.conf.d
    sudo cp -a system-configs/sddm/* /etc/
    sudo chown -R root:root /etc/sddm.conf* 2>/dev/null || true
else
    echo "⚠️  Warning: system-configs/sddm/ not found, skipping SDDM config."
fi

# Set jake_the_dog theme for SDDM Astronaut
if [ -f /usr/share/sddm/themes/sddm-astronaut-theme/Themes/jake_the_dog.conf ]; then
    sudo cp /usr/share/sddm/themes/sddm-astronaut-theme/Themes/jake_the_dog.conf /usr/share/sddm/themes/sddm-astronaut-theme/theme.conf.user
fi

CURRENT_STEP="Enabling services"
echo "[5] Enabling Services and System Optimizations (Needs Sudo)..."
# ZRAM Setup (Virtual Swap)
sudo mkdir -p /etc/systemd/
# Allocate half of RAM size for ZRAM (balanced and safe for all systems, matching Fedora defaults)
ZRAM_SIZE="ram / 2"
echo -e "[zram0]\nzram-size = $ZRAM_SIZE\ncompression-algorithm = zstd" | sudo tee /etc/systemd/zram-generator.conf > /dev/null
sudo systemctl daemon-reload || true
sudo systemctl start systemd-zram-setup@zram0.service || true

# Enable vital services
sudo systemctl enable sddm.service || echo "⚠️ Warning: Failed to enable sddm.service. Your GUI might not start automatically."
sudo systemctl enable bluetooth.service || echo "⚠️ Warning: Failed to enable bluetooth.service."
sudo systemctl enable systemd-timesyncd.service || echo "⚠️ Warning: Failed to enable systemd-timesyncd.service."

# Docker Service Setup
ENABLE_DOCKER="Y"
if [ -t 0 ] && [ -z "$AUTO_INSTALL" ]; then
    echo "⚠️  WARNING: Adding your user to the 'docker' group grants root-equivalent privileges."
    read -p "❓ Enable Docker service & add user to docker group? [Y/n]: " USER_DOCKER_INPUT
    ENABLE_DOCKER=${USER_DOCKER_INPUT:-Y}
fi

if [[ "$ENABLE_DOCKER" =~ ^[Yy]$ ]]; then
    REAL_USER=${SUDO_USER:-$(logname 2>/dev/null || whoami)}
    sudo usermod -aG docker "$REAL_USER" || echo "⚠️ Warning: Failed to add $REAL_USER to docker group."
    sudo systemctl enable docker.service || echo "⚠️ Warning: Failed to enable docker.service."
fi

# UFW Firewall Setup
ENABLE_UFW="Y"
if [ -t 0 ] && [ -z "$AUTO_INSTALL" ]; then
    read -p "❓ Enable UFW Firewall? [Y/n]: " USER_UFW_INPUT
    ENABLE_UFW=${USER_UFW_INPUT:-Y}
fi

if [[ "$ENABLE_UFW" =~ ^[Yy]$ ]]; then
    sudo systemctl enable ufw.service || echo "⚠️ Warning: Failed to enable ufw.service."
    sudo ufw default deny incoming || true
    sudo ufw default allow outgoing || true
    sudo ufw allow ssh || true
    sudo ufw enable || echo "⚠️ Warning: Failed to enable ufw."
fi

touch ~/.NooreldeanOS-installed
echo "✅ Installation Complete! Please reboot your computer."
