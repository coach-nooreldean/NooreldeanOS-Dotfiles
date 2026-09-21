#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS Btrfs Snapshot & Recovery Tool (noor-snap)
# Automatic & Manual System Snapshots with GRUB Boot Integration & Rofi GUI
# ==============================================================================

set -euo pipefail
ORIGINAL_ARGS=("$@")

# Visual styling
CYAN='\033[0;36m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

print_banner() {
  echo -e "${PURPLE}${BOLD}"
  cat << "BANNER"
  _  _                     ___                  
 | \| |___ ___ _ _ ___ ___/ __|_ _  __ _ _ __   
 | .` / _ \ _ \ '_/ -_)___|__ \ ' \/ _` | '_ \  
 |_|\_\___/___/_| \___|   |___/_||_\__,_| .__/  
       Btrfs Bulletproof System Recovery|_|     
BANNER
  echo -e "${RESET}"
}

check_btrfs() {
  local fs_type
  fs_type="$(findmnt -n -o FSTYPE / 2>/dev/null || echo "unknown")"
  if [[ "$fs_type" != "btrfs" ]]; then
    return 1
  fi
  return 0
}

ensure_root() {
  if [[ $EUID -ne 0 ]]; then
    echo -e "${YELLOW}➜ This action requires administrative privileges.${RESET}"
    exec sudo "$0" "${ORIGINAL_ARGS[@]}"
  fi
}

cmd_create() {
  local desc="${1:-Manual snapshot by user}"
  ensure_root

  if ! check_btrfs; then
    echo -e "${RED}[✖] Root filesystem is not Btrfs. Snapshots are only supported on Btrfs.${RESET}"
    exit 1
  fi

  echo -e "${CYAN}➜ Creating system snapshot...${RESET}"
  local snap_id
  snap_id="$(snapper -c root create -t single -d "$desc" --print-number)"
  echo -e "${GREEN}[✔] Snapshot #$snap_id created successfully: '${desc}'${RESET}"

  # Refresh grub-btrfs if installed
  if command -v grub-mkconfig &>/dev/null && [[ -f /boot/grub/grub.cfg ]]; then
    echo -e "${YELLOW}➜ Updating GRUB boot menu with new snapshot...${RESET}"
    grub-mkconfig -o /boot/grub/grub.cfg &>/dev/null || true
    echo -e "${GREEN}[✔] Boot menu updated.${RESET}"
  fi

  if command -v notify-send &>/dev/null && [[ -n "${SUDO_USER:-}" ]]; then
    sudo -u "$SUDO_USER" notify-send -a "NooreldeanOS" -i "system-software-update" \
      "📸 تم حفظ لقطة النظام بنجاح" "رقم اللقطة: #$snap_id\nالوصف: $desc" || true
  fi
}

cmd_list() {
  if ! check_btrfs; then
    echo -e "${RED}[✖] Root filesystem is not Btrfs.${RESET}"
    exit 1
  fi
  print_banner
  snapper -c root list
}

cmd_rollback() {
  local id="${1:-}"
  if [[ -z "$id" ]]; then
    echo -e "${RED}Usage: noor-snap rollback <snapshot_id>${RESET}"
    exit 1
  fi
  ensure_root

  echo -e "${YELLOW}⚠️  WARNING: You are about to restore system to snapshot #$id.${RESET}"
  read -rp "Are you sure you want to proceed? [y/N]: " confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}➜ Performing snapper rollback to #$id...${RESET}"
    snapper -c root rollback "$id"
    if command -v grub-mkconfig &>/dev/null && [[ -f /boot/grub/grub.cfg ]]; then
      echo -e "${YELLOW}➜ Updating GRUB boot menu...${RESET}"
      grub-mkconfig -o /boot/grub/grub.cfg
    fi
    echo -e "${GREEN}${BOLD}[✔ SUCCESS] System restored to snapshot #$id.${RESET}"
    echo -e "${CYAN}Please reboot your computer to boot into the restored state.${RESET}"
  else
    echo -e "${YELLOW}Rollback cancelled.${RESET}"
  fi
}

cmd_delete() {
  local id="${1:-}"
  if [[ -z "$id" ]]; then
    echo -e "${RED}Usage: noor-snap delete <snapshot_id>${RESET}"
    exit 1
  fi
  ensure_root
  echo -e "${CYAN}➜ Deleting snapshot #$id...${RESET}"
  snapper -c root delete "$id"
  echo -e "${GREEN}[✔] Snapshot #$id deleted.${RESET}"
}

cmd_rofi() {
  if ! check_btrfs; then
    if command -v notify-send &>/dev/null; then
      notify-send -a "NooreldeanOS" -u critical -i "dialog-error" \
        "تعذر استخدام اللقطات" "نظام الملفات الحالي ليس Btrfs."
    fi
    echo -e "${RED}[✖] Root filesystem is not Btrfs.${RESET}"
    exit 1
  fi

  local rofi_theme="${HOME}/.config/rofi/snapshots.rasi"
  local rofi_cmd=(rofi -dmenu -i)
  if [[ -f "$rofi_theme" ]]; then
    rofi_cmd+=(-theme "$rofi_theme")
  else
    rofi_cmd+=(-theme-str 'window { width: 660px; border-radius: 18px; } listview { columns: 1; fixed-height: false; }')
  fi

  local choice
  choice="$(printf "📸 أخذ لقطة نظام جديدة (Create Snapshot)\n📋 استعراض اللقطات المحفوظة (List Snapshots)\n🔄 استرجاع النظام للقطة سابقة (Rollback)\n🗑️ حذف لقطة قديمة (Delete Snapshot)\n📊 مساحة تخزين اللقطات (Disk Usage)" | "${rofi_cmd[@]}" -p "🛡️ حماية النظام:")"

  case "$choice" in
    *"Create Snapshot"*)
      local desc
      desc="$("${rofi_cmd[@]}" -p "📝 وصف اللقطة:")"
      if [[ -n "$desc" ]]; then
        ensure_root
        cmd_create "$desc"
      fi
      ;;
    *"List Snapshots"*)
      local snaps
      snaps="$(snapper -c root list | tail -n +3 || echo "لا توجد لقطات")"
      echo "$snaps" | "${rofi_cmd[@]}" -p "📋 اللقطات:" -theme-str 'window { width: 780px; } element-text { font: "JetBrainsMono Nerd Font 12"; }'
      ;;
    *"Rollback"*)
      local id
      id="$("${rofi_cmd[@]}" -p "🔄 رقم اللقطة:")"
      if [[ -n "$id" ]]; then
        kitty -e bash -c "sudo noor-snap rollback '$id'; echo 'Press Enter to close'; read"
      fi
      ;;
    *"Delete Snapshot"*)
      local del_id
      del_id="$("${rofi_cmd[@]}" -p "🗑️ رقم اللقطة:")"
      if [[ -n "$del_id" ]]; then
        ensure_root
        cmd_delete "$del_id"
      fi
      ;;
    *"Disk Usage"*)
      local usage
      usage="$(btrfs filesystem df / 2>/dev/null || echo "Unable to query Btrfs")"
      echo "$usage" | "${rofi_cmd[@]}" -p "📊 مساحة القرص:" -theme-str 'window { width: 680px; } element-text { font: "JetBrainsMono Nerd Font 12"; }'
      ;;
  esac
}

# Main Dispatcher
case "${1:-}" in
  create)
    shift
    cmd_create "$@"
    ;;
  list)
    cmd_list
    ;;
  rollback)
    shift
    cmd_rollback "$@"
    ;;
  delete)
    shift
    cmd_delete "$@"
    ;;
  rofi|gui)
    cmd_rofi
    ;;
  *)
    if [[ -t 0 ]] && [[ $# -eq 0 ]]; then
      print_banner
      echo -e "${BOLD}Usage:${RESET} noor-snap <command> [args]"
      echo -e "  ${CYAN}create [desc]${RESET}   - Create a new manual system snapshot"
      echo -e "  ${CYAN}list${RESET}            - List all existing snapshots"
      echo -e "  ${CYAN}rollback <id>${RESET}   - Safely restore system to snapshot <id>"
      echo -e "  ${CYAN}delete <id>${RESET}     - Delete a specific snapshot"
      echo -e "  ${CYAN}rofi | gui${RESET}      - Open interactive graphical snapshot manager"
    else
      cmd_rofi
    fi
    ;;
esac
