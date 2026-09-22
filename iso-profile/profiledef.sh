#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="nooreldeanos"
iso_label="NOOROS_$(date +%Y%m)"
iso_publisher="Nooreldean <https://github.com/coach-nooreldean>"
iso_application="NooreldeanOS Linux Live/Rescue/Installation Media"
iso_version="$(date +%Y.%m.%d)"
install_dir="arch"
build_modes=('iso')
bootmodes=('bios.syslinux' 'uefi.systemd-boot')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/gshadow"]="0:0:400"
  ["/etc/sudoers.d"]="0:0:750"
  ["/etc/sudoers.d/g_wheel"]="0:0:440"
  ["/root"]="0:0:750"
  ["/usr/local/bin/sys-clean"]="0:0:755"
  ["/usr/local/bin/audio_switcher.sh"]="0:0:755"
  ["/usr/local/bin/wallpaper_switcher.sh"]="0:0:755"
  ["/usr/local/bin/install-nooreldeanos"]="0:0:755"
  ["/usr/local/bin/nooreldeanos-gpu-setup"]="0:0:755"
  ["/usr/local/bin/nooreldeanos-live-setup"]="0:0:755"
  ["/usr/local/bin/noor-snap"]="0:0:755"
  ["/usr/local/bin/display_switcher.sh"]="0:0:755"
)
