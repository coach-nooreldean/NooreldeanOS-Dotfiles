#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure we are in the directory of the script
cd "$(dirname "$0")"

echo "🗑️  Uninstalling NooreldeanOS..."

echo "[1] Restoring previous configuration..."
# Find the latest backup directory
LATEST_BACKUP=$(ls -d ~/.config-backup-* 2>/dev/null | sort -r | head -n 1)

if [ -n "$LATEST_BACKUP" ]; then
    echo "    Found backup at: $LATEST_BACKUP"
    echo "    Restoring your original .config directory..."
    
    # Backup the current (NooreldeanOS) config just in case
    mv ~/.config ~/.config-nooreldeanos-backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
    
    # Restore the backup
    cp -r "$LATEST_BACKUP" ~/.config
    echo "    ✅ Configurations restored successfully."
else
    echo "    ⚠️  No backup directory found (~/.config-backup-*). Skipping configuration restore."
fi

echo "[2] Removing added scripts..."
# Removing the specific scripts we added to ~/scripts
rm -f ~/scripts/system-update.sh
rm -f ~/scripts/system-cleanup.sh
echo "    ✅ Scripts removed."

echo "[3] Cleaning up system services..."
echo "    Note: We are not automatically disabling services (like sddm, bluetooth, docker, ufw, zram) to avoid breaking your system if you relied on them before."
echo "    If you want to disable them manually, you can use: sudo systemctl disable <service_name>"

echo "[4] Packages and Apps..."
echo "    ⚠️  To keep your system stable, this script does NOT automatically uninstall the packages downloaded."
echo "    If you wish to remove the packages we installed, please review the 'pacman-packages.txt' and 'flatpak-packages.txt' files and uninstall them manually using pacman or yay."

echo ""
echo "✅ Uninstallation Complete!"
echo "🔄 Please reboot or log out and log back in to see the changes."
