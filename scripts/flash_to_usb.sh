#!/usr/bin/env bash
set -euo pipefail

DEFAULT_ISO_DIR="/mnt/data3/NooreldeanOS-ISO"
TARGET_DEVICE="${1:-/dev/sde}"

# Locate latest ISO file
ISO_FILE=""
if [ -d "$DEFAULT_ISO_DIR" ]; then
    ISO_FILE=$(find "$DEFAULT_ISO_DIR" -maxdepth 2 -type f -name "nooreldeanos-*.iso" ! -name "*.part" | sort -V | tail -n 1)
fi

# Fallback to Downloads if not found in data3
if [ -z "$ISO_FILE" ] || [ ! -f "$ISO_FILE" ]; then
    ISO_FILE=$(find "$HOME/Downloads" -maxdepth 2 -type f -name "nooreldeanos-*.iso" 2>/dev/null | sort -V | tail -n 1 || true)
fi

echo "=================================================="
echo "      ⚡ NooreldeanOS Live USB Flasher ⚡"
echo "=================================================="
echo ""

if [ -z "$ISO_FILE" ] || [ ! -f "$ISO_FILE" ]; then
    echo "❌ ERROR: No ISO file found (.iso)!"
    echo "Please download it first using: python3 scripts/fast_download.py"
    exit 1
fi

ISO_SIZE=$(du -h "$ISO_FILE" | cut -f1)
echo "📦 ISO File: $ISO_FILE ($ISO_SIZE)"
echo "🎯 Target USB Drive: $TARGET_DEVICE"
echo ""

echo "📋 Currently connected block devices:"
lsblk -o NAME,SIZE,TYPE,TRAN,RM,MODEL,MOUNTPOINTS
echo "=================================================="
echo ""

# Safety check: Block device exists
if [ ! -b "$TARGET_DEVICE" ]; then
    echo "❌ ERROR: Device $TARGET_DEVICE does not exist!"
    echo "Please plug in your USB flash drive and verify the device letter (e.g., /dev/sde)."
    exit 1
fi

# Confirm with user if interactive
if [ -t 0 ]; then
    echo "⚠️  CRITICAL WARNING: ALL DATA on $TARGET_DEVICE will be completely ERASED!"
    read -p "Are you sure you want to flash NooreldeanOS to $TARGET_DEVICE? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "🛑 Flashing cancelled by user."
        exit 0
    fi
fi

echo ""
echo "1️⃣  Unmounting all mounted partitions on $TARGET_DEVICE..."
for part in $(lsblk -lnpo NAME "$TARGET_DEVICE" | tail -n +2); do
    echo "  - Unmounting: $part"
    udisksctl unmount -b "$part" 2>/dev/null || sudo umount "$part" 2>/dev/null || true
done

echo ""
echo "2️⃣  Writing ISO directly to $TARGET_DEVICE..."
echo "⚡ Using direct I/O and 4MB block size for maximum write speed..."

if command -v pkexec >/dev/null 2>&1 && [ -n "${DISPLAY:-}" ]; then
    pkexec dd if="$ISO_FILE" of="$TARGET_DEVICE" bs=4M status=progress conv=fsync oflag=direct
else
    sudo dd if="$ISO_FILE" of="$TARGET_DEVICE" bs=4M status=progress conv=fsync oflag=direct
fi

echo ""
echo "3️⃣  Flushing I/O buffer to USB drive (sync)..."
sync

echo ""
echo "=================================================="
echo "🎉 SUCCESS: NooreldeanOS flashed to $TARGET_DEVICE successfully!"
echo "✨ Your USB flash drive is now bootable."
echo "=================================================="
