#!/hint/bash
# ==============================================================================
# NooreldeanOS Live Session — Auto-start Hyprland on TTY1
# ==============================================================================
# This file auto-launches Hyprland when the liveuser logs in on TTY1.
# Only runs if no Wayland display is already active and we are on VT1.

if [[ -z "${WAYLAND_DISPLAY}" ]] && [[ "${XDG_VTNR}" == "1" ]]; then
    # Set XDG runtime directory for the live session
    export XDG_RUNTIME_DIR="/run/user/$(id -u)"
    mkdir -p "${XDG_RUNTIME_DIR}" 2>/dev/null
    exec Hyprland
fi
