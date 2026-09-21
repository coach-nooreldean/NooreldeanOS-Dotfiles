#!/usr/bin/env bash
# ==============================================================================
# Apply All NooreldeanOS Features, Tools & Themes to the Current Host System
# ==============================================================================

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${PURPLE}${BOLD}"
cat << "BANNER"
  _  _                     _     _                  ___  ___ 
 | \| |___ ___ _ _ ___ ___| | __| |___ __ _ _ _    / _ \/ __|
 | .` / _ \ _ \ '_/ -_) _ \ |/ _` / -_) _` | ' \  | (_) \__ \
 |_|\_\___/___/_| \___|___/_|\__,_\___|__,_|_||_|  \___/|___/
      System-Wide Integration & Host Deployment Engine
BANNER
echo -e "${RESET}"

if [[ $EUID -ne 0 ]]; then
  echo -e "${YELLOW}➜ Elevating privileges to configure system packages and Plymouth...${RESET}"
  exec sudo "$0" "$@"
fi

TARGET_USER="${SUDO_USER:-$USER}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"

echo -e "${CYAN}➜ Step 1: Installing missing system packages (snapper, snap-pac, grub-btrfs, plymouth)...${RESET}"
pacman -S --needed --noconfirm snapper snap-pac grub-btrfs plymouth inotify-tools

echo -e "${CYAN}➜ Step 2: Deploying system-wide CLI tools to /usr/local/bin/...${RESET}"
cp "$SCRIPT_DIR/noor-snap.sh" /usr/local/bin/noor-snap
cp "$SCRIPT_DIR/display_switcher.sh" /usr/local/bin/display_switcher.sh
cp "$SCRIPT_DIR/nooreldeanos-gpu-setup.sh" /usr/local/bin/nooreldeanos-gpu-setup
cp "$SCRIPT_DIR/sys-clean.sh" /usr/local/bin/sys-clean
chmod +x /usr/local/bin/{noor-snap,display_switcher.sh,nooreldeanos-gpu-setup,sys-clean}
echo -e "${GREEN}  ✔ CLI tools installed.${RESET}"

echo -e "${CYAN}➜ Step 3: Configuring NooreldeanOS Plymouth Boot Splash...${RESET}"
bash "$SCRIPT_DIR/setup-plymouth.sh"

echo -e "${CYAN}➜ Step 4: Configuring Snapper Btrfs root snapshot template...${RESET}"
if findmnt -n -o FSTYPE / | grep -q "btrfs"; then
  mkdir -p /etc/snapper/configs /etc/conf.d
  if [[ ! -f /etc/snapper/configs/root ]]; then
    snapper create-config / || true
  fi
  cat << 'SNAPCONF' > /etc/snapper/configs/root
# NooreldeanOS Snapper Config
SUBVOLUME="/"
FSTYPE="btrfs"
QGROUP=""
SPACE_LIMIT="0.2"
FREE_LIMIT="0.2"
ALLOW_USERS=""
ALLOW_GROUPS="wheel"
SYNC_ACL="yes"
BACKGROUND_COMPARISON="yes"
NUMBER_CLEANUP="yes"
NUMBER_MIN_AGE="1800"
NUMBER_LIMIT="10"
NUMBER_LIMIT_IMPORTANT="5"
TIMELINE_CREATE="no"
TIMELINE_CLEANUP="yes"
EMPTY_PRE_POST_CLEANUP="yes"
EMPTY_PRE_POST_MIN_AGE="1800"
SNAPCONF
  echo "SNAPPER_CONFIGS=\"root\"" > /etc/conf.d/snapper
  systemctl enable --now snapper-cleanup.timer || true
  systemctl enable --now grub-btrfsd || true
  echo -e "${GREEN}  ✔ Snapper and grub-btrfsd active.${RESET}"
fi

echo -e "${CYAN}➜ Step 5: Running GPU Auto-Detection & Tuning...${RESET}"
/usr/local/bin/nooreldeanos-gpu-setup

echo -e "${CYAN}➜ Step 6: Ensuring user configurations and permissions...${RESET}"
chown -R "$TARGET_USER:$TARGET_USER" "$TARGET_HOME/.config/hypr" "$TARGET_HOME/.config/swaync" "$TARGET_HOME/.local/bin"

echo -e "\n${GREEN}${BOLD}[🎉 ALL DONE] Every single feature of NooreldeanOS is now installed and active on your system!${RESET}"
echo -e "${CYAN}You can now enjoy:${RESET}"
echo -e "  • ${PURPLE}Super + Shift + S${RESET} ➜ Btrfs Snapshots Manager (noor-snap)"
echo -e "  • ${PURPLE}Super + Shift + D${RESET} ➜ Display & 144Hz/240Hz Switcher"
echo -e "  • ${PURPLE}Super + A${RESET}         ➜ Audio & Bluetooth Switcher"
echo -e "  • ${PURPLE}Super + L${RESET}         ➜ Glass Acrylic Hyprlock"
echo -e "  • ${PURPLE}SwayNC 8-Grid${RESET}     ➜ Control Center\n"
