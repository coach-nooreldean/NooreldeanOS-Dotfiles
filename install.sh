#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -eo pipefail

# Ensure we are in the directory of the script using absolute path
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DOTFILES_DIR"

# Source configurations and logger
# shellcheck source=lib/config.conf
source "lib/config.conf"
# shellcheck source=lib/logger.sh
source "lib/logger.sh"

# Prevent running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please do not run this script as root! Run it as your normal user."
    exit 1
fi

# Clean up any leftover temp sudoers from a previous interrupted run
sudo rm -f /etc/sudoers.d/99-temp-nopasswd 2>/dev/null || true

# Ask for sudo password upfront
log_info "Please enter your password to grant sudo access for the installation:"
sudo -v
# Keep-alive: update existing sudo time stamp if set, otherwise do nothing.
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &
SUDO_KEEP_ALIVE_PID=$!

# Ensure the keep-alive is killed on exit or interruption
trap 'kill $SUDO_KEEP_ALIVE_PID 2>/dev/null; [ -n "$YAY_TMP" ] && rm -rf "$YAY_TMP" 2>/dev/null' EXIT SIGINT

# Error handler: show which step failed before exiting
trap 'kill $SUDO_KEEP_ALIVE_PID 2>/dev/null; [ -n "$YAY_TMP" ] && rm -rf "$YAY_TMP" 2>/dev/null; log_error "Installation failed at step: $CURRENT_STEP (line $LINENO)\n💡 Tip: Check your internet connection or any specific error messages above.\n🔄 You can safely re-run this script after fixing the issue."' ERR

log_step "Checking internet connection..."
ping -c 1 -W 3 1.1.1.1 &> /dev/null || curl -Is --connect-timeout 3 https://archlinux.org &> /dev/null || { log_error "No internet connection."; exit 1; }

CURRENT_STEP="Initialization"
log_step "Installing NooreldeanOS..."

# Source modules
# shellcheck source=lib/core_install.sh
source "lib/core_install.sh"
# shellcheck source=lib/backup.sh
source "lib/backup.sh"
# shellcheck source=lib/symlinks.sh
source "lib/symlinks.sh"
# shellcheck source=lib/services.sh
source "lib/services.sh"

# Execute functions
install_packages
backup_configs
restore_configs
enable_services

touch ~/.NooreldeanOS-installed
log_success "Installation Complete! Please reboot your computer."
