#!/bin/bash
echo "🚀 Installing NooreldeanOS..."
echo "[1] Installing all programs (This will take time)..."
yay -S --needed - < pacman-packages.txt
if [ -f flatpak-packages.txt ]; then
    flatpak install -y $(cat flatpak-packages.txt)
fi

echo "[2] Restoring Configurations..."
cp -r .config/* ~/.config/
cp -r home/icons/* ~/.local/share/icons/ 2>/dev/null
cp -r home/.bash* ~/
cp -r scripts/* ~/
chmod +x ~/*.sh
mkdir -p ~/.local/share/applications
cp -r applications/* ~/.local/share/applications/

echo "[3] Restoring System Configs (Needs Sudo)..."
sudo cp -r system-configs/sddm/* /etc/

echo "✅ Installation Complete! Please reboot your computer."
