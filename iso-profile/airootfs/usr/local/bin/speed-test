#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS Speed Test CLI Launcher
# ==============================================================================

if [ -f "$HOME/.config/speed-test/run.sh" ]; then
    exec "$HOME/.config/speed-test/run.sh" "$@"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    DOTFILES_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
    exec python3 "${DOTFILES_DIR}/.config/speed-test/main.py" "$@"
fi
