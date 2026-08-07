#!/bin/bash

# ==============================================================================
# Backup Configurations Module
# ==============================================================================

backup_configs() {
    # shellcheck disable=SC2034
    CURRENT_STEP="Backing up configurations"
    if [ -f ~/.NooreldeanOS-installed ]; then
        log_info "Skipping backup because NooreldeanOS is already installed."
    else
        log_step "Backing up existing configurations..."
        BACKUP_DIR=~/.NooreldeanOS-backup-$(date +%Y%m%d-%H%M%S)
        mkdir -p "$BACKUP_DIR/.config" "$BACKUP_DIR/local-share" "$BACKUP_DIR/home"
        log_info "Backing up specific dotfiles and directories that will be modified..."

        safe_backup() {
            if [ -e "$1" ]; then
                cp -a "$1" "$2" 2>/dev/null || log_warning "Failed to backup $1"
            fi
        }

        # Backup .config subdirectories that we will overwrite
        for item in .config/*; do
            if [ -e "$item" ]; then
                basename=$(basename "$item")
                safe_backup "$HOME/.config/$basename" "$BACKUP_DIR/.config/"
            fi
        done

        # Backup other directories being overwritten
        if [ -d "home/icons" ]; then
            safe_backup "$HOME/.local/share/icons" "$BACKUP_DIR/local-share/"
        fi

        if [ -d "$HOME/scripts" ]; then
            safe_backup "$HOME/scripts" "$BACKUP_DIR/home/"
        fi

        # Backup home dotfiles that will be overwritten
        if [ -d "home" ]; then
            for f in home/.bash*; do
                if [ -e "$f" ]; then
                    fname=$(basename "$f")
                    safe_backup "$HOME/$fname" "$BACKUP_DIR/home/"
                fi
            done
        fi

        if [ -d "applications" ]; then
            safe_backup "$HOME/.local/share/applications" "$BACKUP_DIR/local-share/"
        fi

        log_success "Backup saved to: $BACKUP_DIR"
    fi
}
