#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS Dynamic Display & Refresh Rate Switcher (Super + Shift + D)
# Instant on-the-fly resolution, refresh rate (144Hz/240Hz), and UI scaling tuning
# ==============================================================================

set -euo pipefail

MONITORS_CONF="$HOME/.config/hypr/monitors.conf"

notify() {
  local title="$1"
  local msg="$2"
  if command -v notify-send &>/dev/null; then
    notify-send -a "NooreldeanOS" -i "video-display" "$title" "$msg"
  fi
}

save_monitor_config() {
  local mon_name="$1"
  local mon_res="$2"
  local mon_hz="$3"
  local mon_pos="$4"
  local mon_scale="$5"

  mkdir -p "$(dirname "$MONITORS_CONF")"
  
  # Remove old line for this monitor if present
  if [[ -f "$MONITORS_CONF" ]]; then
    grep -v "monitor = $mon_name," "$MONITORS_CONF" > "$MONITORS_CONF.tmp" || true
    mv "$MONITORS_CONF.tmp" "$MONITORS_CONF"
  fi

  echo "monitor = $mon_name, ${mon_res}@${mon_hz}, $mon_pos, $mon_scale" >> "$MONITORS_CONF"
}

# Fetch monitors JSON
if ! command -v hyprctl &>/dev/null; then
  notify "خطأ" "hyprctl غير متوفر في الجلسة الحالية."
  exit 1
fi

MONITORS_JSON="$(hyprctl monitors -j 2>/dev/null || echo "[]")"
NUM_MONITORS="$(echo "$MONITORS_JSON" | jq '. | length')"

if [[ "$NUM_MONITORS" -eq 0 ]]; then
  notify "شاشات العرض" "لم يتم العثور على أي شاشات نشطة."
  exit 1
fi

# Step 1: Select Monitor (if more than 1)
SELECTED_NAME=""
if [[ "$NUM_MONITORS" -gt 1 ]]; then
  MON_LIST=""
  for i in $(seq 0 $((NUM_MONITORS - 1))); do
    NAME="$(echo "$MONITORS_JSON" | jq -r ".[$i].name")"
    MODEL="$(echo "$MONITORS_JSON" | jq -r ".[$i].model")"
    WIDTH="$(echo "$MONITORS_JSON" | jq -r ".[$i].width")"
    HEIGHT="$(echo "$MONITORS_JSON" | jq -r ".[$i].height")"
    HZ="$(echo "$MONITORS_JSON" | jq -r ".[$i].refreshRate" | cut -d'.' -f1)"
    MON_LIST+="${NAME} — ${MODEL} (${WIDTH}x${HEIGHT} @ ${HZ}Hz)\n"
  done

  CHOICE="$(echo -e "$MON_LIST" | sed '/^$/d' | rofi -dmenu -p "🖥️ اختر الشاشة (Select Monitor):" -theme-str 'window {width: 480px;}')"
  if [[ -z "$CHOICE" ]]; then
    exit 0
  fi
  SELECTED_NAME="$(echo "$CHOICE" | cut -d' ' -f1)"
else
  SELECTED_NAME="$(echo "$MONITORS_JSON" | jq -r '.[0].name')"
fi

# Query current properties of selected monitor
MON_DATA="$(echo "$MONITORS_JSON" | jq ".[] | select(.name == \"$SELECTED_NAME\")")"
CURR_WIDTH="$(echo "$MON_DATA" | jq -r '.width')"
CURR_HEIGHT="$(echo "$MON_DATA" | jq -r '.height')"
CURR_HZ="$(echo "$MON_DATA" | jq -r '.refreshRate' | cut -d'.' -f1)"
CURR_SCALE="$(echo "$MON_DATA" | jq -r '.scale')"
CURR_X="$(echo "$MON_DATA" | jq -r '.x')"
CURR_Y="$(echo "$MON_DATA" | jq -r '.y')"
CURR_POS="${CURR_X}x${CURR_Y}"
AVAILABLE_MODES="$(echo "$MON_DATA" | jq -r '.availableModes[]?')"

# Step 2: Main Menu for Selected Monitor
ACTION="$(printf "⚡ معدل الإنعاش (Refresh Rate: %sHz)\n📐 دقة الشاشة (Resolution: %sx%s)\n🔍 مقياس الواجهة (UI Scale: %s)\n⏹️ إيقاف / تشغيل الشاشة (Toggle Power)" "$CURR_HZ" "$CURR_WIDTH" "$CURR_HEIGHT" "$CURR_SCALE" | rofi -dmenu -p "⚙️ إعدادات [$SELECTED_NAME]:" -theme-str 'window {width: 420px;}')"

case "$ACTION" in
  *"Refresh Rate"*)
    # Extract unique refresh rates for current resolution
    HZ_LIST=""
    RATES="$(echo "$AVAILABLE_MODES" | grep -E "^${CURR_WIDTH}x${CURR_HEIGHT}@" | cut -d'@' -f2 | sed 's/Hz//' | cut -d'.' -f1 | sort -nru || true)"
    if [[ -z "$RATES" ]]; then
      # Fallback standard gaming rates
      RATES="240\n165\n144\n120\n75\n60"
    fi

    for r in $RATES; do
      if [[ "$r" == "$CURR_HZ" ]]; then
        HZ_LIST+="★ ${r}Hz (الحالي)\n"
      else
        HZ_LIST+="${r}Hz\n"
      fi
    done

    TARGET_HZ="$(echo -e "$HZ_LIST" | sed '/^$/d' | rofi -dmenu -p "⚡ اختر التردد (Refresh Rate):" -theme-str 'window {width: 340px;}')"
    if [[ -n "$TARGET_HZ" ]]; then
      CLEAN_HZ="$(echo "$TARGET_HZ" | grep -oE '[0-9]+' | head -n 1)"
      hyprctl keyword monitor "${SELECTED_NAME}, ${CURR_WIDTH}x${CURR_HEIGHT}@${CLEAN_HZ}, ${CURR_POS}, ${CURR_SCALE}"
      save_monitor_config "$SELECTED_NAME" "${CURR_WIDTH}x${CURR_HEIGHT}" "$CLEAN_HZ" "$CURR_POS" "$CURR_SCALE"
      notify "⚡ تم تحديث تردد الشاشة" "${SELECTED_NAME} الآن تعمل بتردد ${CLEAN_HZ}Hz"
    fi
    ;;

  *"Resolution"*)
    # Extract unique resolutions
    RES_LIST=""
    RESOLUTIONS="$(echo "$AVAILABLE_MODES" | cut -d'@' -f1 | sort -u | sort -t'x' -k1,1nr -k2,2nr || true)"
    if [[ -z "$RESOLUTIONS" ]]; then
      RESOLUTIONS="3840x2160\n2560x1440\n1920x1080\n1680x1050\n1366x768\n1280x720"
    fi

    for res in $RESOLUTIONS; do
      if [[ "$res" == "${CURR_WIDTH}x${CURR_HEIGHT}" ]]; then
        RES_LIST+="★ $res (الحالية)\n"
      else
        RES_LIST+="$res\n"
      fi
    done

    TARGET_RES="$(echo -e "$RES_LIST" | sed '/^$/d' | rofi -dmenu -p "📐 اختر الدقة (Resolution):" -theme-str 'window {width: 360px;}')"
    if [[ -n "$TARGET_RES" ]]; then
      CLEAN_RES="$(echo "$TARGET_RES" | grep -oE '[0-9]+x[0-9]+')"
      hyprctl keyword monitor "${SELECTED_NAME}, ${CLEAN_RES}@${CURR_HZ}, ${CURR_POS}, ${CURR_SCALE}"
      save_monitor_config "$SELECTED_NAME" "$CLEAN_RES" "$CURR_HZ" "$CURR_POS" "$CURR_SCALE"
      notify "📐 تم تغيير دقة الشاشة" "${SELECTED_NAME} الآن بدقة ${CLEAN_RES}"
    fi
    ;;

  *"UI Scale"*)
    SCALES="1.0  (100% - دقة عادية)\n1.25 (125% - موصى به لـ 2K)\n1.5  (150% - موصى به لـ 4K)\n1.75 (175%)\n2.0  (200% - HiDPI)"
    TARGET_SCALE="$(echo -e "$SCALES" | rofi -dmenu -p "🔍 اختر مقياس الواجهة (Scale):" -theme-str 'window {width: 380px;}')"
    if [[ -n "$TARGET_SCALE" ]]; then
      CLEAN_SCALE="$(echo "$TARGET_SCALE" | awk '{print $1}')"
      hyprctl keyword monitor "${SELECTED_NAME}, ${CURR_WIDTH}x${CURR_HEIGHT}@${CURR_HZ}, ${CURR_POS}, ${CLEAN_SCALE}"
      save_monitor_config "$SELECTED_NAME" "${CURR_WIDTH}x${CURR_HEIGHT}" "$CURR_HZ" "$CURR_POS" "$CLEAN_SCALE"
      notify "🔍 تم تحديث مقياس الواجهة" "مقياس شاشة ${SELECTED_NAME}: ${CLEAN_SCALE}x"
    fi
    ;;

  *"Toggle Power"*)
    hyprctl keyword monitor "${SELECTED_NAME}, disable"
    notify "⏹️ تم إيقاف الشاشة" "تم تعطيل شاشة ${SELECTED_NAME}"
    ;;
esac
