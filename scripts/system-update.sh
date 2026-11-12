#!/bin/bash
echo -e "\033[1;36mStarting System Update...\033[0m"

echo -e "\n\033[1;33m>>> 1. Updating system packages (pacman + AUR)...\033[0m"
yay -Syu

echo -e "\n\033[1;33m>>> 2. Updating Flatpak apps (including Craft suite)...\033[0m"
if command -v flatpak &> /dev/null; then
    flatpak update -y
else
    echo "Flatpak not installed, skipping."
fi

echo -e "\n\033[1;33m>>> 3. Checking and updating ArtCraft Launcher...\033[0m"
if command -v curl &> /dev/null && command -v jq &> /dev/null; then
    LATEST_JSON=$(curl -s --connect-timeout 5 --max-time 10 https://api.github.com/repos/storytold/craft-launcher/releases/latest 2>/dev/null || true)
    LATEST_TAG=$(echo "$LATEST_JSON" | jq -r .tag_name 2>/dev/null || true)

    if [[ -n "$LATEST_TAG" && "$LATEST_TAG" != "null" ]]; then
        LATEST_VER="${LATEST_TAG#v}"
        CURRENT_VER=""
        if command -v artcraft-launcher &>/dev/null; then
            CURRENT_VER=$(artcraft-launcher --version 2>/dev/null | awk '{print $2}')
        fi

        if [[ "$CURRENT_VER" != "$LATEST_VER" ]]; then
            echo -e "\033[0;36mFound new ArtCraft Launcher release: ${LATEST_VER} (Installed: ${CURRENT_VER:-none})\033[0m"
            TARBALL_URL="https://github.com/storytold/craft-launcher/releases/download/${LATEST_TAG}/artcraft-launcher-${LATEST_VER}-linux-x86_64.tar.gz"
            TMP_TAR="/tmp/artcraft-launcher-${LATEST_VER}.tar.gz"

            echo -e "Downloading ArtCraft ${LATEST_VER}..."
            if curl -sL --connect-timeout 10 -o "$TMP_TAR" "$TARBALL_URL"; then
                INSTALL_DIR="$HOME/.local/opt/artcraft-launcher-${LATEST_VER}"
                mkdir -p "$INSTALL_DIR"
                tar -zxf "$TMP_TAR" -C "$INSTALL_DIR" --strip-components=1

                mkdir -p "$HOME/.local/bin"
                ln -sf "$INSTALL_DIR/bin/artcraft-launcher" "$HOME/.local/bin/artcraft-launcher"
                chmod +x "$HOME/.local/bin/artcraft-launcher" "$INSTALL_DIR/bin/artcraft-launcher"

                if [[ -f "$HOME/.local/share/applications/artcraft-launcher.desktop" ]]; then
                    sed -i "s|artcraft-launcher-[0-9.]*|artcraft-launcher-${LATEST_VER}|g" "$HOME/.local/share/applications/artcraft-launcher.desktop"
                fi

                rm -f "$TMP_TAR"
                echo -e "\033[0;32m✔ ArtCraft Launcher successfully updated to ${LATEST_VER}!\033[0m"
            else
                echo -e "\033[0;31m✖ Failed to download ArtCraft update.\033[0m"
            fi
        else
            echo -e "\033[0;32m✔ ArtCraft Launcher is up to date (${CURRENT_VER}).\033[0m"
        fi
    else
        echo "Could not fetch latest ArtCraft release (offline or rate limited), skipping."
    fi
else
    echo "curl or jq not found, skipping ArtCraft update check."
fi

echo -e "\n\033[1;32mSystem Update Complete!\033[0m"
read -r -p "Press Enter to close this window..."
