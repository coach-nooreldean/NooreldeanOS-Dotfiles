#!/bin/bash

# ==============================================================================
# Symlinks and Restoration Module
# ==============================================================================

restore_configs() {
    # shellcheck disable=SC2034
    CURRENT_STEP="Restoring configurations"
    log_step "Restoring Configurations..."
    mkdir -p ~/.config ~/.local/share/icons ~/.local/share/applications ~/scripts

    log_prompt "Do you want to use Symlinks for your dotfiles?"
    log_info "   (Choose 'y' if you plan to edit configs and push to Github, choose 'n' for a standard stable install)"
    read -r -p "    Use Symlinks? [y/N]: " USE_SYMLINKS

    if [[ "$USE_SYMLINKS" =~ ^[Yy]$ ]]; then
        log_info "Creating Symlinks (Developer Mode)..."
        safe_symlink() {
            local src="$1"
            local dest_dir="$2"
            shopt -s dotglob
            for item in "$src"/*; do
                [ -e "$item" ] || continue
                local target
                target="$dest_dir/$(basename "$item")"
                if [ -d "$target" ] && [ ! -L "$target" ]; then
                    rm -rf "$target"
                fi
                ln -sfn "$item" "$dest_dir/" 2>/dev/null || true
            done
            shopt -u dotglob
        }

        if [ -d ".config" ]; then safe_symlink "$DOTFILES_DIR/.config" ~/.config; fi
        if [ -d "home/icons" ]; then safe_symlink "$DOTFILES_DIR/home/icons" ~/.local/share/icons; fi
        if [ -d "home" ]; then safe_symlink "$DOTFILES_DIR/home" ~/; fi
        if [ -d "scripts" ]; then safe_symlink "$DOTFILES_DIR/scripts" ~/scripts; fi
        if [ -d "scripts" ]; then chmod +x ~/scripts/*.sh 2>/dev/null || true; fi
        if [ -d "wallpapers" ]; then safe_symlink "$DOTFILES_DIR/wallpapers" ~/wallpapers; fi
        if [ -d "applications" ]; then safe_symlink "$DOTFILES_DIR/applications" ~/.local/share/applications; fi
    elif command -v rsync &> /dev/null; then
        log_info "Copying files using rsync..."
        if [ -d ".config" ]; then rsync -a .config/ ~/.config/ 2>/dev/null || true; fi
        if [ -d "home/icons" ]; then rsync -a home/icons/ ~/.local/share/icons/ 2>/dev/null || true; fi
        if [ -d "home" ]; then rsync -a home/.bash* ~/ 2>/dev/null || true; fi
        if [ -d "scripts" ]; then rsync -a scripts/ ~/scripts/ 2>/dev/null || true; fi
        if [ -d "scripts" ]; then chmod +x ~/scripts/*.sh 2>/dev/null || true; fi
        if [ -d "wallpapers" ]; then rsync -a wallpapers/ ~/wallpapers/ 2>/dev/null || true; fi
        if [ -d "applications" ]; then rsync -a applications/ ~/.local/share/applications/ 2>/dev/null || true; fi
    else
        # Fallback if rsync is somehow not installed
        log_info "Copying files using cp..."
        shopt -s dotglob
        if [ -d ".config" ]; then cp -a .config/* ~/.config/ 2>/dev/null || true; fi
        if [ -d "home/icons" ]; then cp -a home/icons/* ~/.local/share/icons/ 2>/dev/null || true; fi
        if [ -d "home" ]; then cp -a home/.bash* ~/ 2>/dev/null || true; fi
        if [ -d "scripts" ]; then cp -a scripts/* ~/scripts/ 2>/dev/null || true; fi
        if [ -d "scripts" ]; then chmod +x ~/scripts/*.sh 2>/dev/null || true; fi
        if [ -d "wallpapers" ]; then cp -a wallpapers ~/ 2>/dev/null || true; fi
        if [ -d "applications" ]; then cp -a applications/* ~/.local/share/applications/ 2>/dev/null || true; fi
        shopt -u dotglob
    fi

    # Pre-generate Pywal colors from the default wallpaper so Hyprland has valid colors on first boot
    log_info "Generating color scheme from default wallpaper..."
    DEFAULT_WALLPAPER="$HOME/wallpapers/Pastel-Window.png"
    if [ ! -f "$DEFAULT_WALLPAPER" ]; then
        DEFAULT_WALLPAPER=$(find ~/wallpapers -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) 2>/dev/null | head -n 1 || true)
    fi
    if command -v wal &> /dev/null && [ -n "$DEFAULT_WALLPAPER" ]; then
        wal -i "$DEFAULT_WALLPAPER" -n -e -q 2>/dev/null || true
        if command -v python3 &> /dev/null && [ -f ~/.config/hypr/scripts/pywal_hyprland_sync.py ]; then
            python3 ~/.config/hypr/scripts/pywal_hyprland_sync.py 2>/dev/null || true
        fi
    fi

    # Failsafe: Ensure Waybar and Hyprland don't crash if Pywal failed to run (e.g., missing wallpapers)
    mkdir -p ~/.cache/wal
    touch ~/.cache/wal/colors-waybar.css
    if [ ! -f ~/.cache/wal/colors.json ]; then
        echo '{"special": {"background": "#1e1e2e", "foreground": "#cdd6f4"}, "colors": {"color0": "#45475a", "color1": "#f38ba8", "color2": "#a6e3a1", "color3": "#f9e2af", "color4": "#89b4fa", "color5": "#f5c2e7", "color6": "#94e2d5", "color7": "#bac2de"}}' > ~/.cache/wal/colors.json
    fi
}
