#!/usr/bin/env bash
# ==============================================================================
# NooreldeanOS GPU Auto-Detection & Optimization Service
# Detects AMD, Intel, and NVIDIA hardware; automatically configures Wayland,
# kernel DRM parameters, and Smart Hybrid Offload (prime-run).
# ==============================================================================

set -euo pipefail

LOG_FILE="/var/log/nooreldeanos-gpu.log"
STATUS_JSON="/var/log/nooreldeanos-gpu.json"
MARKER_FILE="/var/log/nooreldeanos-gpu.done"

# Colors for CLI output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
RESET='\033[0m'

log() {
  local msg="$1"
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "[$ts] $msg" >> "$LOG_FILE"
  echo -e "$msg"
}

print_banner() {
  echo -e "${PURPLE}${BOLD}"
  cat << "BANNER"
   ___ ___ _   _   ___      _           _   
  / __| _ \ | | | |   \ ___| |_ ___  __| |_ 
 | (_ |  _/ |_| | | |) / -_)  _/ -_)/ _|  _|
  \___|_|  \___/  |___/\___|\__\___|\__|\__|
    NooreldeanOS Graphics Architecture Engine
BANNER
  echo -e "${RESET}"
}

if [[ "${1:-}" == "--status" ]]; then
  print_banner
  if [[ -f "$STATUS_JSON" ]]; then
    echo -e "${GREEN}Active GPU Architecture Profile:${RESET}"
    cat "$STATUS_JSON"
  else
    echo -e "${YELLOW}GPU setup has not run yet. Detecting on-the-fly:${RESET}"
    lspci -nnk | grep -iE 'vga|3d|display' || true
  fi
  exit 0
fi

if [[ "${1:-}" == "--notify" ]]; then
  # Notification runner called by user session
  if [[ -f "$STATUS_JSON" ]] && command -v notify-send &>/dev/null; then
    MODE="$(grep '"mode":' "$STATUS_JSON" | cut -d'"' -f4 || echo "Optimized")"
    GPUS="$(grep '"primary_gpu":' "$STATUS_JSON" | cut -d'"' -f4 || echo "Hardware Detected")"
    notify-send -a "NooreldeanOS" -u normal -i "video-display" \
      "🎮 ضبط بطاقة الرسومات بنجاح" \
      "تم تفعيل: $GPUS\nالوضع: $MODE"
  fi
  exit 0
fi

# Need root for actual system configuration
if [[ $EUID -ne 0 ]]; then
  echo -e "${YELLOW}Root privileges required. Elevating...${RESET}"
  exec sudo "$0" "$@"
fi

mkdir -p "$(dirname "$LOG_FILE")"
print_banner >> "$LOG_FILE"
log "${CYAN}➜ Probing PCI Bus for graphics hardware...${RESET}"

GPU_RAW="$(lspci -nnk | grep -iE 'vga|3d|display' || true)"
log "Detected raw controllers:\n$GPU_RAW"

HAS_NVIDIA=false
HAS_AMD=false
HAS_INTEL=false

if echo "$GPU_RAW" | grep -qi "nvidia"; then
  HAS_NVIDIA=true
fi
if echo "$GPU_RAW" | grep -qiE "amd|radeon|advanced micro"; then
  HAS_AMD=true
fi
if echo "$GPU_RAW" | grep -qi "intel"; then
  HAS_INTEL=true
fi

PRIMARY_GPU="Unknown"
MODE="Standard Mesa"
HYBRID=false

# Determine profile
if [[ "$HAS_NVIDIA" == true && ("$HAS_AMD" == true || "$HAS_INTEL" == true) ]]; then
  HYBRID=true
  PRIMARY_GPU="NVIDIA Optimus Hybrid"
  MODE="Smart Hybrid Offload (prime-run)"
elif [[ "$HAS_NVIDIA" == true ]]; then
  PRIMARY_GPU="NVIDIA Dedicated"
  MODE="Dedicated High Performance"
elif [[ "$HAS_AMD" == true ]]; then
  PRIMARY_GPU="AMD Radeon"
  MODE="Pure Open Source Mesa (RADV)"
elif [[ "$HAS_INTEL" == true ]]; then
  PRIMARY_GPU="Intel Graphics"
  MODE="Pure Open Source Mesa (ANV)"
fi

log "${GREEN}  ✔ Primary Architecture:${RESET} $PRIMARY_GPU"
log "${GREEN}  ✔ Configured Mode:${RESET} $MODE"

# Apply system optimizations
mkdir -p /etc/environment.d /etc/modprobe.d

if [[ "$HAS_NVIDIA" == true ]]; then
  log "${CYAN}➜ Configuring NVIDIA Wayland & DRM settings...${RESET}"
  
  # Kernel module configuration
  cat << 'MOD' > /etc/modprobe.d/nvidia.conf
# NooreldeanOS NVIDIA DRM Configuration
options nvidia-drm modeset=1 fbdev=1
options nvidia "NVreg_DynamicPowerManagement=0x02"
options nvidia "NVreg_PreserveVideoMemoryAllocations=1"
MOD

  # Environment variables for Wayland & hardware acceleration
  cat << 'ENV' > /etc/environment.d/10-nooreldeanos-nvidia.conf
# NVIDIA Wayland Architecture
LIBVA_DRIVER_NAME=nvidia
XDG_SESSION_TYPE=wayland
GBM_BACKEND=nvidia-drm
__GLX_VENDOR_LIBRARY_NAME=nvidia
NVD_BACKEND=direct
ELECTRON_OZONE_PLATFORM_HINT=auto
ENV

  # Enable persistence daemon if available
  if systemctl list-unit-files | grep -q "nvidia-persistenced.service"; then
    systemctl enable nvidia-persistenced.service || true
  fi

elif [[ "$HAS_AMD" == true ]]; then
  log "${CYAN}➜ Configuring AMD Radeon Mesa acceleration...${RESET}"
  cat << 'ENV' > /etc/environment.d/10-nooreldeanos-amd.conf
# AMD Radeon Wayland Acceleration
LIBVA_DRIVER_NAME=radeonsi
VDPAU_DRIVER=radeonsi
AMD_VULKAN_ICD=RADV
ELECTRON_OZONE_PLATFORM_HINT=auto
ENV

elif [[ "$HAS_INTEL" == true ]]; then
  log "${CYAN}➜ Configuring Intel Graphics acceleration...${RESET}"
  cat << 'ENV' > /etc/environment.d/10-nooreldeanos-intel.conf
# Intel Graphics Wayland Acceleration
LIBVA_DRIVER_NAME=iHD
VDPAU_DRIVER=va_gl
ELECTRON_OZONE_PLATFORM_HINT=auto
ENV
fi

# Write status JSON
cat << JSON > "$STATUS_JSON"
{
  "primary_gpu": "$PRIMARY_GPU",
  "has_nvidia": $HAS_NVIDIA,
  "has_amd": $HAS_AMD,
  "has_intel": $HAS_INTEL,
  "is_hybrid": $HYBRID,
  "mode": "$MODE",
  "configured_at": "$(date -Iseconds)"
}
JSON

touch "$MARKER_FILE"
log "${GREEN}${BOLD}[✔ SUCCESS] GPU Auto-Detection & Configuration Completed!${RESET}"
