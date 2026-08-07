#!/bin/bash

# ==============================================================================
# Services and System Optimizations Module
# ==============================================================================

enable_services() {
    # shellcheck disable=SC2034
    CURRENT_STEP="Restoring system configs"
    log_step "Restoring System Configs (Needs Sudo)..."
    if [ -d system-configs/sddm ]; then
        sudo mkdir -p /etc/sddm.conf.d
        sudo cp -a system-configs/sddm/* /etc/
        sudo chown -R root:root /etc/sddm.conf* 2>/dev/null || true
    else
        log_warning "system-configs/sddm/ not found, skipping SDDM config."
    fi

    # Set jake_the_dog theme for SDDM Astronaut
    if [ -f /usr/share/sddm/themes/sddm-astronaut-theme/Themes/jake_the_dog.conf ]; then
        sudo cp /usr/share/sddm/themes/sddm-astronaut-theme/Themes/jake_the_dog.conf /usr/share/sddm/themes/sddm-astronaut-theme/theme.conf.user
    fi

    # shellcheck disable=SC2034
    CURRENT_STEP="Enabling services"
    log_step "Enabling Services and System Optimizations (Needs Sudo)..."
    # ZRAM Setup (Virtual Swap)
    sudo mkdir -p /etc/systemd/
    echo -e "[zram0]\nzram-size = ${ZRAM_SIZE}\ncompression-algorithm = zstd" | sudo tee /etc/systemd/zram-generator.conf > /dev/null
    sudo systemctl daemon-reload || true
    sudo systemctl start systemd-zram-setup@zram0.service || true

    # Enable vital services
    sudo systemctl enable sddm.service || log_warning "Failed to enable sddm.service. Your GUI might not start automatically."
    sudo systemctl enable bluetooth.service || log_warning "Failed to enable bluetooth.service."
    sudo systemctl enable systemd-timesyncd.service || log_warning "Failed to enable systemd-timesyncd.service."

    # Docker Service Setup
    if [ -t 0 ] && [ -z "$AUTO_INSTALL" ]; then
        log_warning "Adding your user to the 'docker' group grants root-equivalent privileges."
        log_prompt "Enable Docker service & add user to docker group? [Y/n]: "
        read -r USER_DOCKER_INPUT
        ENABLE_DOCKER=${USER_DOCKER_INPUT:-Y}
    fi

    if [[ "$ENABLE_DOCKER" =~ ^[Yy]$ ]]; then
        REAL_USER=${SUDO_USER:-$(logname 2>/dev/null || whoami)}
        sudo usermod -aG docker "$REAL_USER" || log_warning "Failed to add $REAL_USER to docker group."
        sudo systemctl enable docker.service || log_warning "Failed to enable docker.service."
    fi

    # UFW Firewall Setup
    if [ -t 0 ] && [ -z "$AUTO_INSTALL" ]; then
        log_prompt "Enable UFW Firewall? [Y/n]: "
        read -r USER_UFW_INPUT
        ENABLE_UFW=${USER_UFW_INPUT:-Y}
    fi

    if [[ "$ENABLE_UFW" =~ ^[Yy]$ ]]; then
        sudo systemctl enable ufw.service || log_warning "Failed to enable ufw.service."
        sudo ufw default deny incoming || true
        sudo ufw default allow outgoing || true
        sudo ufw allow ssh || true
        sudo ufw enable || log_warning "Failed to enable ufw."
    fi
}
