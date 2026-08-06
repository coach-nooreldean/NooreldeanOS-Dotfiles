#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Error handler: show which step failed before exiting
trap 'echo "\n❌ ERROR: Installation failed at step: $CURRENT_STEP (line $LINENO)"; echo "   Check the output above for details."' ERR
CURRENT_STEP="Initialization"

# Ensure we are in the directory of the script
cd "$(dirname "$0")"

echo "🚀 Installing NooreldeanOS..."
CURRENT_STEP="Installing packages"
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
if [ -f flatpak-packages.txt ] && [ -s flatpak-packages.txt ]; then
    if ! command -v flatpak &> /dev/null; then
        echo "📦 'flatpak' is not installed. Installing flatpak..."
        sudo pacman -S --needed --noconfirm flatpak
    fi
    flatpak install -y $(cat flatpak-packages.txt) || true
fi

CURRENT_STEP="Backing up configurations"
echo "[2] Backing up existing configurations..."
BACKUP_DIR=~/.config-backup-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"
cp -r ~/.config/* "$BACKUP_DIR/" 2>/dev/null || true
echo "    Backup saved to: $BACKUP_DIR"

CURRENT_STEP="Restoring configurations"
echo "[3] Restoring Configurations..."
mkdir -p ~/.config ~/.local/share/icons ~/.local/share/applications
cp -r .config/* ~/.config/ || true
cp -r home/icons/* ~/.local/share/icons/ 2>/dev/null || true
cp -r home/.bash* ~/ || true
mkdir -p ~/scripts
cp -r scripts/* ~/scripts/ || true
chmod +x ~/scripts/*.sh || true
cp -r wallpapers ~/ || true
cp -r applications/* ~/.local/share/applications/ || true

echo "    Adjusting hardcoded paths for the current user ($USER)..."
find ~/.config ~/scripts ~/.local/share/applications ~/wallpapers -type f -exec sed -i "s|/home/nooreldean|$HOME|g" {} + 2>/dev/null || true

# Pre-generate Pywal colors from the default wallpaper so Hyprland has valid colors on first boot
echo "    Generating color scheme from default wallpaper..."
if command -v wal &> /dev/null && [ -f ~/wallpapers/Pastel-Window.png ]; then
    wal -i ~/wallpapers/Pastel-Window.png -n -e -q 2>/dev/null || true
    python3 ~/.config/hypr/scripts/pywal_hyprland_sync.py 2>/dev/null || true
fi

CURRENT_STEP="Restoring system configs"
echo "[4] Restoring System Configs (Needs Sudo)..."
if [ -d system-configs/sddm ]; then
    sudo cp -r system-configs/sddm/* /etc/
else
    echo "⚠️  Warning: system-configs/sddm/ not found, skipping SDDM config."
fi

CURRENT_STEP="Enabling services"
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
