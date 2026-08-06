#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure we are in the directory of the script
cd "$(dirname "$0")"

echo "🚀 Installing NooreldeanOS..."
echo "[1] Installing all programs (This will take time)..."

# Check and install yay if not present
if ! command -v yay &> /dev/null; then
    echo "📦 'yay' is not installed. Installing yay..."
    sudo pacman -S --needed --noconfirm git base-devel
    git clone https://aur.archlinux.org/yay.git /tmp/yay
    (cd /tmp/yay && makepkg -si --noconfirm)
    rm -rf /tmp/yay
fi

yay -S --needed - < pacman-packages.txt
if [ -f flatpak-packages.txt ]; then
    if ! command -v flatpak &> /dev/null; then
        echo "📦 'flatpak' is not installed. Installing flatpak..."
        sudo pacman -S --needed --noconfirm flatpak
    fi
    flatpak install -y $(cat flatpak-packages.txt) || true
fi

echo "[2] Backing up existing configurations..."
BACKUP_DIR=~/.config-backup-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"
cp -r ~/.config/* "$BACKUP_DIR/" 2>/dev/null || true
echo "    Backup saved to: $BACKUP_DIR"

echo "[3] Restoring Configurations..."
mkdir -p ~/.config ~/.local/share/icons ~/.local/share/applications
cp -r .config/* ~/.config/ || true
cp -r home/icons/* ~/.local/share/icons/ 2>/dev/null || true
cp -r home/.bash* ~/ || true
cp -r scripts/* ~/ || true
cp -r wallpapers ~/ || true
chmod +x ~/*.sh || true
cp -r applications/* ~/.local/share/applications/ || true

echo "[4] Restoring System Configs (Needs Sudo)..."
sudo cp -r system-configs/sddm/* /etc/

echo "[5] Enabling Services and System Optimizations (Needs Sudo)..."
# ZRAM Setup (Virtual Swap)
sudo mkdir -p /etc/systemd/
echo -e "[zram0]\nzram-size = ram / 2\ncompression-algorithm = zstd" | sudo tee /etc/systemd/zram-generator.conf > /dev/null

# Add current user to Docker group
sudo usermod -aG docker $USER || true

# Enable vital services
sudo systemctl enable sddm.service || true
sudo systemctl enable bluetooth.service || true
sudo systemctl enable docker.service || true
sudo systemctl enable systemd-timesyncd.service || true

# Setup UFW Firewall
sudo systemctl enable ufw.service || true
sudo ufw default deny incoming || true
sudo ufw default allow outgoing || true
sudo ufw enable || true

echo "✅ Installation Complete! Please reboot your computer."
