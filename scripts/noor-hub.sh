#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS Control Hub & Quick Settings (مركز تحكم النظام)
# Powered by Rofi & Pywal
# ==============================================================================

set -euo pipefail

ROFI_THEME="${HOME}/.config/rofi/hub.rasi"
ROFI_CMD=(rofi -dmenu -i -p "⚡ مركز التحكم")
if [[ -f "$ROFI_THEME" ]]; then
  ROFI_CMD+=(-theme "$ROFI_THEME")
fi

declare -A ACTIONS=(
  ["🎨  مغير الخلفيات والثيم (Wallpaper Picker)"]="~/.config/hypr/scripts/wallpaper_switcher.sh"
  ["  إدارة أجهزة البلوتوث (Bluetooth Manager)"]="bash -c '$HOME/.config/bluetooth-manager/run.sh'"
  ["🔊  مخرج الصوت والأجهزة (Audio Switcher)"]="~/.config/hypr/scripts/audio_switcher.sh"
  ["🖥️  إعدادات الشاشات والتردد (Display Switcher)"]="display_switcher.sh"
  ["🚀  فحص سرعة الإنترنت (Speed Test)"]="bash -c '$HOME/.config/speed-test/run.sh'"
  ["💾  إدارة نقاط الاستعادة (Btrfs Snapshots)"]="noor-snap rofi"
  ["🧹  تنظيف الكاش والملفات المؤقتة (System Cleaner)"]="kitty --title 'تنظيف النظام' -e sys-clean"
  ["📦  تحديث النظام الشامل (System Update)"]="kitty --title 'تحديث النظام' -e ~/scripts/system-update.sh"
  ["🎬  محول ومضغط الفيديو (Video Converter)"]="python3 ~/.config/video-converter/main.py"
  ["💽  تهيئة وتنسيق الفلاشات (Drive Formatter)"]="python3 ~/.config/drive-formatter/main.py"
  ["⚡  وضع الأداء العالي / توفير الطاقة (Power Profile)"]="TOGGLE_POWER"
  ["🔒  قفل الشاشة (Lock Screen)"]="hyprlock"
  ["🚪  قائمة الخروج وإيقاف التشغيل (Power Menu)"]="wlogout"
)

ITEMS=(
  "🎨  مغير الخلفيات والثيم (Wallpaper Picker)"
  "  إدارة أجهزة البلوتوث (Bluetooth Manager)"
  "🔊  مخرج الصوت والأجهزة (Audio Switcher)"
  "🖥️  إعدادات الشاشات والتردد (Display Switcher)"
  "🚀  فحص سرعة الإنترنت (Speed Test)"
  "💾  إدارة نقاط الاستعادة (Btrfs Snapshots)"
  "🧹  تنظيف الكاش والملفات المؤقتة (System Cleaner)"
  "📦  تحديث النظام الشامل (System Update)"
  "🎬  محول ومضغط الفيديو (Video Converter)"
  "💽  تهيئة وتنسيق الفلاشات (Drive Formatter)"
  "⚡  وضع الأداء العالي / توفير الطاقة (Power Profile)"
  "🔒  قفل الشاشة (Lock Screen)"
  "🚪  قائمة الخروج وإيقاف التشغيل (Power Menu)"
)

MENU_INPUT=$(printf "%s\n" "${ITEMS[@]}")
SELECTED=$(printf "%s" "$MENU_INPUT" | "${ROFI_CMD[@]}" || true)

[[ -z "$SELECTED" ]] && exit 0

CMD="${ACTIONS[$SELECTED]:-}"
[[ -z "$CMD" ]] && exit 0

if [[ "$CMD" == "TOGGLE_POWER" ]]; then
  if command -v powerprofilesctl &>/dev/null; then
    CURRENT=$(powerprofilesctl get 2>/dev/null || echo "balanced")
    if [[ "$CURRENT" == "performance" ]]; then
      powerprofilesctl set balanced 2>/dev/null || true
      notify-send -a "NooreldeanOS" -i "battery" "وضع الطاقة" "تم التحويل إلى: المتوازن (Balanced)"
    else
      powerprofilesctl set performance 2>/dev/null || true
      notify-send -a "NooreldeanOS" -i "battery-charging" "وضع الطاقة" "تم تفعيل: الأداء الأقصى (Performance 🚀)"
    fi
  else
    notify-send -a "NooreldeanOS" "وضع الطاقة" "أداة power-profiles-daemon غير مفعلة"
  fi
  exit 0
fi

eval "$CMD &"
