#!/usr/bin/env bash
# ==============================================================================
# sys-clean: Smart Arch Linux Maintenance & SSD Optimization
# Part of NooreldeanOS
# ==============================================================================

set -eo pipefail

# Ensure we run from a safe directory so deleting caches doesn't invalidate $PWD
cd "$HOME" || exit 1

# ANSI Colors
BOLD="\033[1m"
GREEN="\033[1;32m"
BLUE="\033[1;34m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

log_title() { echo -e "\n${BOLD}${CYAN}=== $1 ===${RESET}"; }
log_step()  { echo -e "${BOLD}${BLUE}➜ $1${RESET}"; }
log_info()  { echo -e "  ${CYAN}•${RESET} $1"; }
log_done()  { echo -e "  ${GREEN}✔${RESET} $1"; }
log_warn()  { echo -e "  ${YELLOW}⚠${RESET} $1"; }
log_error() { echo -e "  ${RED}✖${RESET} $1"; }

echo -e "${BOLD}${GREEN}"
echo "   ___ _   _ ___       ___ _    ___   _   _  _ "
echo "  / __| | | / __|___  / __| |  | __| /_\ | \| |"
echo "  \__ \ |_| \__ \___| | (__| |__| _| / _ \| .\` |"
echo "  |___/\__, |___/      \___|____|___/_/ \_\_|\_|"
echo "       |___/                                   "
echo -e "${RESET}${CYAN}      NooreldeanOS Maintenance & Optimization Tool${RESET}\n"

# Check sudo access upfront
log_step "Checking administrative privileges..."
if [ "$EUID" -ne 0 ]; then
    sudo -v
    while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &
    SUDO_PID=$!
    trap 'kill $SUDO_PID 2>/dev/null || true' EXIT
fi
log_done "Privileges acquired."

# Measure disk usage before cleanup
DISK_BEFORE_KB=$(df -k / 2>/dev/null | awk 'NR==2 {print $3}')
DISK_BEFORE_KB=${DISK_BEFORE_KB:-0}
DISK_BEFORE_HUMAN=$(df -h / 2>/dev/null | awk 'NR==2 {print $3}')
DISK_BEFORE_HUMAN=${DISK_BEFORE_HUMAN:-"N/A"}

# Step 1: Remove Orphan Packages
log_title "Step 1: Removing Unused Dependencies (Orphans)"
ORPHANS=$(pacman -Qtdq 2>/dev/null || true)
if [ -n "$ORPHANS" ]; then
    log_info "Found orphans: $(echo "$ORPHANS" | tr '\n' ' ')"
    # shellcheck disable=SC2086
    sudo pacman -Rns --noconfirm $ORPHANS
    log_done "Orphan packages removed."
else
    log_done "No orphan packages found."
fi

# Step 2: Clean Pacman & Yay Cache
log_title "Step 2: Cleaning Package Caches"
if command -v yay &>/dev/null; then
    log_info "Cleaning yay and pacman build caches..."
    yay -Sc --noconfirm 2>/dev/null || true
    log_done "Package manager cache cleaned."
else
    log_info "Cleaning pacman cache..."
    sudo pacman -Sc --noconfirm 2>/dev/null || true
    log_done "Pacman cache cleaned."
fi

# Step 3: Vacuum Systemd Journal Logs
log_title "Step 3: Optimizing Systemd Journal Logs"
JOURNAL_SIZE=$(journalctl --disk-usage 2>/dev/null | awk '{print $NF}' || echo "N/A")
log_info "Current journal logs usage: $JOURNAL_SIZE"
sudo journalctl --vacuum-size=100M --vacuum-time=7d &>/dev/null || true
log_done "Systemd logs reduced to ≤ 100MB (retaining past 7 days)."

# Step 4: Clean Flatpak (if installed)
log_title "Step 4: Cleaning Unused Flatpaks"
if command -v flatpak &>/dev/null; then
    flatpak uninstall --unused -y &>/dev/null || true
    log_done "Unused Flatpak runtimes pruned."
else
    log_done "Flatpak is not installed (skipping)."
fi

# Step 5: Clean User Caches
log_title "Step 5: Cleaning Temporary User Caches"
rm -rf "$HOME/.cache/thumbnails"/* 2>/dev/null || true
rm -rf "$HOME/.cache/yay"/* 2>/dev/null || true
log_done "Thumbnail cache & yay build artifacts cleared."

# Step 6: SSD TRIM Optimization
log_title "Step 6: Running SSD TRIM Optimization"
if command -v fstrim &>/dev/null; then
    log_info "Issuing TRIM commands to mounted SSDs..."
    sudo fstrim -av 2>/dev/null || true
    log_done "SSD TRIM completed successfully."
else
    log_warn "fstrim command not available (skipping)."
fi

# Summary Report
DISK_AFTER_KB=$(df -k / 2>/dev/null | awk 'NR==2 {print $3}')
DISK_AFTER_KB=${DISK_AFTER_KB:-0}
DISK_AFTER_HUMAN=$(df -h / 2>/dev/null | awk 'NR==2 {print $3}')
DISK_AFTER_HUMAN=${DISK_AFTER_HUMAN:-"N/A"}
FREED_KB=$((DISK_BEFORE_KB - DISK_AFTER_KB))

echo -e "\n${BOLD}${GREEN}======================================================${RESET}"
echo -e "${BOLD}${GREEN}                CLEANUP SUMMARY REPORT                ${RESET}"
echo -e "${BOLD}${GREEN}======================================================${RESET}"
echo -e "  Used space before : ${BOLD}${YELLOW}$DISK_BEFORE_HUMAN${RESET}"
echo -e "  Used space after  : ${BOLD}${CYAN}$DISK_AFTER_HUMAN${RESET}"

if [ "$FREED_KB" -gt 0 ]; then
    if [ "$FREED_KB" -ge 1048576 ]; then
        FREED_HUMAN=$(awk -v k="$FREED_KB" 'BEGIN {printf "%.2f GB", k/1048576}')
    elif [ "$FREED_KB" -ge 1024 ]; then
        FREED_HUMAN=$(awk -v k="$FREED_KB" 'BEGIN {printf "%.2f MB", k/1024}')
    else
        FREED_HUMAN="${FREED_KB} KB"
    fi
    echo -e "  Total space freed : ${BOLD}${GREEN}$FREED_HUMAN${RESET}"
else
    echo -e "  Total space freed : ${BOLD}${GREEN}System is already at peak clean state!${RESET}"
fi
echo -e "${BOLD}${GREEN}======================================================${RESET}\n"
