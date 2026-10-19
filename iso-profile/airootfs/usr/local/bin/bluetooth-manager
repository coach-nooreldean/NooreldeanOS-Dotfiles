#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS Bluetooth Manager CLI Launcher
# ==============================================================================

if [ -f "$HOME/.config/bluetooth-manager/run.sh" ]; then
    exec "$HOME/.config/bluetooth-manager/run.sh" "$@"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    DOTFILES_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
    exec python3 "${DOTFILES_DIR}/.config/bluetooth-manager/main.py" "$@"
fi
