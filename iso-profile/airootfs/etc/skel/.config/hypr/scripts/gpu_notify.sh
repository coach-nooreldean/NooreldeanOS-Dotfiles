#!/usr/bin/env bash
# Notify user about detected GPU configuration on login

sleep 3
NOTIFIED_FILE="$HOME/.cache/nooreldeanos-gpu-notified"

if [[ ! -f "$NOTIFIED_FILE" ]] && [[ -f "/var/log/nooreldeanos-gpu.json" ]]; then
  if command -v /usr/local/bin/nooreldeanos-gpu-setup &>/dev/null; then
    /usr/local/bin/nooreldeanos-gpu-setup --notify || true
  fi
  mkdir -p "$HOME/.cache"
  touch "$NOTIFIED_FILE"
fi
