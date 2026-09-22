#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS Archiso Customization Hook
# Executed by mkarchiso inside chroot right after package installation
# ==============================================================================
set -euo pipefail

# Copy NooreldeanOS custom Calamares configs over default package configs
if [[ -d "/etc/calamares-custom" ]]; then
    echo "[NooreldeanOS] Installing custom Calamares configuration..."
    mkdir -p /etc/calamares
    cp -rf /etc/calamares-custom/* /etc/calamares/
fi
