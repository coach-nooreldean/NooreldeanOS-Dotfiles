#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS Plymouth Boot Splash Setup & Preview Tool
# Applies the ultra-modern glowing boot splash to Arch Linux / NooreldeanOS
# ==============================================================================

set -euo pipefail

# Visual styling
CYAN='\033[0;36m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
THEME_DIR="$REPO_DIR/plymouth-theme"
DEST_THEME_DIR="/usr/share/plymouth/themes/nooreldeanos"

echo -e "${PURPLE}${BOLD}"
cat << "BANNER"
  _  _                     _     _                  ___  ___ 
 | \| |___ ___ _ _ ___ ___| | __| |___ __ _ _ _    / _ \/ __|
 | .` / _ \ _ \ '_/ -_) _ \ |/ _` / -_) _` | ' \  | (_) \__ \
 |_|\_\___/___/_| \___|___/_|\__,_\___|__,_|_||_|  \___/|___/
           Boot Splash Architecture & Configuration Tool
BANNER
echo -e "${RESET}"

# Verify root privileges
if [[ $EUID -ne 0 ]]; then
  echo -e "${YELLOW}➜ This script requires administrative privileges to configure Plymouth.${RESET}"
  exec sudo "$0" "$@"
fi

if [[ "${1:-}" == "--test" ]]; then
  echo -e "${CYAN}➜ Testing NooreldeanOS Plymouth Splash for 6 seconds...${RESET}"
  if ! command -v plymouthd &>/dev/null; then
    echo -e "${RED}[✖] plymouth is not installed. Please install it first.${RESET}"
    exit 1
  fi
  plymouthd --debug --debug-file=/tmp/plymouth-debug.log
  plymouth --show-splash
  for ((i=0; i<6; i++)); do
    sleep 1
  done
  plymouth --quit
  echo -e "${GREEN}[✔] Plymouth splash preview completed.${RESET}"
  exit 0
fi

echo -e "${CYAN}➜ Step 1: Checking dependencies...${RESET}"
if ! pacman -Qi plymouth &>/dev/null; then
  echo -e "${YELLOW}  • Installing plymouth...${RESET}"
  pacman -S --noconfirm --needed plymouth
else
  echo -e "${GREEN}  ✔ plymouth is already installed.${RESET}"
fi

echo -e "${CYAN}➜ Step 2: Installing NooreldeanOS theme assets...${RESET}"
mkdir -p "$DEST_THEME_DIR"
cp -rf "$THEME_DIR/"* "$DEST_THEME_DIR/"
echo -e "${GREEN}  ✔ Theme installed to $DEST_THEME_DIR${RESET}"

echo -e "${CYAN}➜ Step 3: Setting NooreldeanOS as the active boot splash...${RESET}"
mkdir -p /etc/plymouth
cat << 'CONF' > /etc/plymouth/plymouthd.conf
[Daemon]
Theme=nooreldeanos
ShowDelay=0
DeviceTimeout=8
CONF

if command -v plymouth-set-default-theme &>/dev/null; then
  plymouth-set-default-theme -R nooreldeanos || true
fi

echo -e "${CYAN}➜ Step 4: Configuring mkinitcpio initramfs hooks...${RESET}"
if [[ -d /etc/mkinitcpio.conf.d ]]; then
  cat << 'HOOK' > /etc/mkinitcpio.conf.d/plymouth.conf
# Added by NooreldeanOS Setup
HOOKS=(base udev plymouth autodetect modconf kms keyboard keymap consolefont block filesystems fsck)
HOOK
  echo -e "${GREEN}  ✔ Added drop-in hook to /etc/mkinitcpio.conf.d/plymouth.conf${RESET}"
fi

echo -e "${YELLOW}➜ Regenerating initramfs with linux-zen / default kernel...${RESET}"
if command -v mkinitcpio &>/dev/null; then
  mkinitcpio -P
fi

echo -e "\n${GREEN}${BOLD}[✔ SUCCESS] NooreldeanOS Boot Splash installed and active!${RESET}"
echo -e "${CYAN}Tip: To preview the splash without rebooting, run:${RESET} sudo bash scripts/setup-plymouth.sh --test\n"
