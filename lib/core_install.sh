#!/bin/bash

# ==============================================================================
# Core Packages Installation Module
# ==============================================================================

install_packages() {
    # shellcheck disable=SC2034
    CURRENT_STEP="Installing packages"
    log_step "Installing all programs (This will take time)..."

    # Check and install yay if not present
    if ! command -v yay &> /dev/null; then
        log_info "'yay' is not installed. Installing yay-bin (Pre-compiled for speed)..."
        sudo pacman -S --needed --noconfirm git base-devel
        YAY_TMP=$(mktemp -d)
        git clone https://aur.archlinux.org/yay-bin.git "$YAY_TMP"
        (cd "$YAY_TMP" && makepkg -si --noconfirm)
        rm -rf "$YAY_TMP"
    fi

    if [ -f pacman-packages.txt ] && [ -s pacman-packages.txt ]; then
        readarray -t PACMAN_PKGS < <(cat pacman-packages.txt | tr -d '\r' | grep -v '^\s*#' | grep -v '^\s*$' || true)
        if [ "${#PACMAN_PKGS[@]}" -gt 0 ]; then
            log_info "Installing pacman and AUR packages..."
            if ! yay -S --needed --noconfirm --answerclean All --answerdiff None --answeredit None "${PACMAN_PKGS[@]}"; then
                log_warning "Some packages failed to install together. Attempting to install them one by one..."
                for pkg in "${PACMAN_PKGS[@]}"; do
                    yay -S --needed --noconfirm --answerclean All --answerdiff None --answeredit None "$pkg" || log_error "Failed to install $pkg, skipping..."
                done
            fi
        fi
    fi

    if [ -f flatpak-packages.txt ] && [ -s flatpak-packages.txt ]; then
        readarray -t FLATPAK_PKGS < <(cat flatpak-packages.txt | tr -d '\r' | grep -v '^\s*#' | grep -v '^\s*$' || true)
        if [ "${#FLATPAK_PKGS[@]}" -gt 0 ]; then
            if ! command -v flatpak &> /dev/null; then
                log_info "'flatpak' is not installed. Installing flatpak..."
                sudo pacman -S --needed --noconfirm flatpak
            fi
            log_info "Enabling Flathub repository..."
            sudo flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true
            log_info "Attempting to install all flatpaks in batch for faster resolution..."
            if ! sudo flatpak install -y --noninteractive flathub "${FLATPAK_PKGS[@]}"; then
                log_warning "Batch install failed, falling back to individual installation..."
                for pkg in "${FLATPAK_PKGS[@]}"; do
                    sudo flatpak install -y --noninteractive flathub "$pkg" || log_error "Failed to install flatpak $pkg, skipping..."
                done
            fi
        fi
    fi
}
