#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS ISO Builder
# Builds a bootable Arch Linux Live ISO with Calamares and Hyprland
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROFILE_DIR="${REPO_DIR}/iso-profile"
OUT_DIR="${REPO_DIR}/out"
WORK_DIR="/tmp/nooreldeanos-build"

COLOR_CYAN='\033[0;36m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

log() {
  echo -e "${COLOR_CYAN}[NooreldeanOS-ISO]${COLOR_RESET} $1"
}

success() {
  echo -e "${COLOR_GREEN}[✔ SUCCESS]${COLOR_RESET} $1"
}

warn() {
  echo -e "${COLOR_YELLOW}[⚠ WARNING]${COLOR_RESET} $1"
}

error() {
  echo -e "${COLOR_RED}[✖ ERROR]${COLOR_RESET} $1" >&2
  exit 1
}

# Check mode flag
if [[ "${1:-}" == "--check" || "${1:-}" == "--dry-run" ]]; then
  log "Checking NooreldeanOS Archiso Profile structure..."

  [[ -f "${PROFILE_DIR}/profiledef.sh" ]] || error "Missing profiledef.sh"
  [[ -f "${PROFILE_DIR}/packages.x86_64" ]] || error "Missing packages.x86_64"
  [[ -f "${PROFILE_DIR}/pacman.conf" ]] || error "Missing pacman.conf"
  [[ -d "${PROFILE_DIR}/airootfs" ]] || error "Missing airootfs directory"

  success "Archiso profile structure is valid and ready for mkarchiso!"
  exit 0
fi

# Ensure root privileges for ISO generation
if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  error "mkarchiso requires root privileges. Please run with sudo: sudo bash scripts/build-iso.sh"
fi

# Check for archiso tool
if ! command -v mkarchiso >/dev/null 2>&1; then
  warn "archiso package not found."
  log "Installing archiso via pacman..."
  pacman -Sy --noconfirm archiso
fi

mkdir -p "${OUT_DIR}"
mkdir -p "${WORK_DIR}"

log "Preparing wallpapers bundle inside live skeleton..."
WALLPAPERS_SRC="${REPO_DIR}/wallpapers"
WALLPAPERS_DEST="${PROFILE_DIR}/airootfs/etc/skel/wallpapers"

if [[ -d "${WALLPAPERS_SRC}" ]]; then
  mkdir -p "${WALLPAPERS_DEST}"
  cp -rn "${WALLPAPERS_SRC}"/* "${WALLPAPERS_DEST}/" 2>/dev/null || true
fi

# Ensure permissions on executable scripts in profile
chmod +x "${PROFILE_DIR}/profiledef.sh"
chmod +x "${PROFILE_DIR}/airootfs/usr/local/bin/"* 2>/dev/null || true
chmod +x "${PROFILE_DIR}/airootfs/root/customize_airootfs.sh" 2>/dev/null || true

log "Starting ISO compilation via mkarchiso..."
log "Profile: ${PROFILE_DIR}"
log "Output:  ${OUT_DIR}"
log "Working: ${WORK_DIR}"

mkarchiso -v -w "${WORK_DIR}" -o "${OUT_DIR}" "${PROFILE_DIR}"

# Clean up dynamically copied wallpapers from git tracked tree
rm -rf "${WALLPAPERS_DEST}"

# Compute SHA256 checksums
log "Computing SHA256 checksums for generated ISOs..."
cd "${OUT_DIR}"
for iso_file in *.iso; do
  if [[ -f "$iso_file" ]]; then
    sha256sum "$iso_file" > "${iso_file}.sha256"
    success "Generated: ${OUT_DIR}/${iso_file}"
    success "Checksum:  ${OUT_DIR}/${iso_file}.sha256"
  fi
done

success "NooreldeanOS ISO build completed successfully!"
