#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS Audio Output & Bluetooth Switcher
# Uses WirePlumber (wpctl), bluetoothctl, and Rofi with Pywal theme integration
# ==============================================================================

set -euo pipefail

ROFI_THEME="${HOME}/.config/rofi/audio.rasi"

# Ensure rofi theme exists, fallback if not
ROFI_CMD=(rofi -dmenu -i -p "🔊 مخرج الصوت")
if [[ -f "$ROFI_THEME" ]]; then
  ROFI_CMD+=(-theme "$ROFI_THEME")
fi

# 1. Parse sinks from wpctl status
# Filter between Audio Sinks and Sources
declare -a SINK_IDS=()
declare -a SINK_LABELS=()
declare -a SINK_NAMES=()
declare -a SINK_ICONS=()

while IFS= read -r line; do
  # Extract numeric ID
  sink_id=$(echo "$line" | grep -oE '[0-9]+\.' | head -n 1 | tr -d '.')
  [[ -z "$sink_id" ]] && continue

  # Check if active default sink (marked with asterisk *)
  is_active=0
  if echo "$line" | grep -q '\*'; then
    is_active=1
  fi

  # Extract clean device name
  name=$(echo "$line" | sed -E 's/.*[0-9]+\.\s+//; s/\s+\[vol:.*//' | xargs)
  [[ -z "$name" ]] && continue

  # Assign friendly emoji icon
  icon="🔊"
  notify_icon="audio-speakers"
  if echo "$name" | grep -qiE "hdmi|displayport"; then
    icon="📺"
    notify_icon="video-display"
  elif echo "$name" | grep -qiE "headphone|headset|earphone"; then
    icon="🎧"
    notify_icon="audio-headphones"
  elif echo "$name" | grep -qiE "bluez|bluetooth"; then
    icon=""
    notify_icon="bluetooth-active"
  fi

  label="${icon}  ${name}"
  if [[ "$is_active" -eq 1 ]]; then
    label="${label}   ✔ (نشط)"
  fi

  SINK_IDS+=("$sink_id")
  SINK_LABELS+=("$label")
  SINK_NAMES+=("$name")
  SINK_ICONS+=("$notify_icon")

done < <(wpctl status 2>/dev/null | sed -e '1,/Audio/d' -e '/Video/,$d' | sed -n '/Sinks:/,/Sources:/p' | grep -E '\s+[0-9]+\.')

# 2. Check for paired Bluetooth audio devices
declare -a BT_MACS=()
declare -a BT_LABELS=()

if systemctl is-active --quiet bluetooth 2>/dev/null; then
  while IFS= read -r bt_line; do
    mac=$(echo "$bt_line" | awk '{print $2}')
    bt_name=$(echo "$bt_line" | cut -d ' ' -f 3- | xargs)
    if [[ -n "$mac" && -n "$bt_name" ]]; then
      BT_MACS+=("$mac")
      BT_LABELS+=("  اتصال: ${bt_name} (Bluetooth)")
    fi
  done < <(timeout 1 bluetoothctl devices 2>/dev/null || true)
fi

# 3. Build Rofi Menu
MENU_CONTENT=""
if [[ "${#SINK_LABELS[@]}" -gt 0 ]]; then
  for label in "${SINK_LABELS[@]}"; do
    MENU_CONTENT+="${label}\n"
  done
fi

if [[ "${#BT_LABELS[@]}" -gt 0 ]]; then
  for bt_label in "${BT_LABELS[@]}"; do
    MENU_CONTENT+="${bt_label}\n"
  done
fi

MENU_CONTENT+="⚙️  إدارة أجهزة البلوتوث (Bluetooth Control)"

# 4. Display Menu
SELECTED=$(printf "%b" "$MENU_CONTENT" | "${ROFI_CMD[@]}" || true)
[[ -z "$SELECTED" ]] && exit 0

# 5. Handle Selection
# Check if user selected Bluetooth manager
if [[ "$SELECTED" == *"إدارة أجهزة البلوتوث"* ]]; then
  kitty --title "إدارة البلوتوث" -e bluetoothctl &
  exit 0
fi

# Check if user selected a Bluetooth device connection
if [[ "${#BT_LABELS[@]}" -gt 0 ]]; then
  for i in "${!BT_LABELS[@]}"; do
    if [[ "$SELECTED" == "${BT_LABELS[i]}" ]]; then
      target_mac="${BT_MACS[i]}"
      notify-send -a "NooreldeanOS" -u low -i "bluetooth-active" "البلوتوث" "جاري الاتصال بـ ${target_mac}..."
      bluetoothctl connect "$target_mac" || true
      exit 0
    fi
  done
fi

# Check if user selected a Sink to switch to
if [[ "${#SINK_LABELS[@]}" -gt 0 ]]; then
  for i in "${!SINK_LABELS[@]}"; do
    if [[ "$SELECTED" == "${SINK_LABELS[i]}" ]]; then
      target_id="${SINK_IDS[i]}"
      target_name="${SINK_NAMES[i]}"
      target_icon="${SINK_ICONS[i]}"

      wpctl set-default "$target_id"
      notify-send -a "NooreldeanOS" -u low -i "$target_icon" "مخرج الصوت" "تم التحويل إلى: ${target_name}"
      exit 0
    fi
  done
fi
