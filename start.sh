#!/bin/bash
# NooreldeanOS Arch Linux Automatic Installer
set -e

# Error handler: show which step failed before exiting
CURRENT_STEP="Initialization"
trap 'echo "\n❌ ERROR: Installation failed at step: $CURRENT_STEP (line $LINENO)"; echo "   Check the output above for details."' ERR

echo "🚀 Welcome to the NooreldeanOS Automatic Installer!"
echo "⚠️ WARNING: This will ERASE EVERYTHING on the selected disk."

# Pre-flight checks
if [ ! -d /sys/firmware/efi ]; then
    echo "❌ Error: System is NOT booted in UEFI mode!"
    echo "   NooreldeanOS requires UEFI. Please reboot in UEFI mode."
    exit 1
fi

if ! ping -c 1 -W 3 archlinux.org &> /dev/null; then
    echo "❌ Error: No internet connection detected!"
    echo "   Please connect to the internet first (use 'iwctl' for WiFi)."
    exit 1
fi

# List available disks
echo "Available disks:"
lsblk -d -p -n -l -o NAME,SIZE,MODEL | grep -E '/dev/sd|/dev/nvme|/dev/vd'

echo -n "Enter the disk to install on (e.g. /dev/sda or /dev/nvme0n1): "
read DISK

if [ ! -b "$DISK" ]; then
    echo "❌ Error: Disk $DISK not found!"
    exit 1
fi

echo "⚙️ Choose Partitioning Method:"
echo "1) 🧹 Auto-Wipe & Partition (ERASES ENTIRE DISK - 1GB EFI, Rest Root)"
echo "2) 🛠️ Manual Partitioning (Opens cfdisk to create partitions manually)"
read -p "Choice [1/2]: " PART_CHOICE

if [ "$PART_CHOICE" == "1" ]; then
    echo "⚠️ Are you absolutely sure you want to WIPEOUT $DISK? (type 'yes' to confirm)"
    read CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi

    echo "🔄 Wiping and partitioning $DISK..."
    wipefs -af "$DISK"
    sgdisk -Z "$DISK"
    sgdisk -n 1:0:+1G -t 1:ef00 -c 1:"EFI System" "$DISK"
    sgdisk -n 2:0:0 -t 2:8300 -c 2:"Linux Root" "$DISK"
    partprobe "$DISK"
    sleep 2

    if [[ $DISK == *"nvme"* ]] || [[ $DISK == *"loop"* ]] || [[ $DISK == *"mmcblk"* ]]; then
        PART_EFI="${DISK}p1"
        PART_ROOT="${DISK}p2"
    else
        PART_EFI="${DISK}1"
        PART_ROOT="${DISK}2"
    fi

    echo "🔄 Formatting partitions..."
    mkfs.fat -F32 "$PART_EFI"
    mkfs.ext4 -F "$PART_ROOT"
    
elif [ "$PART_CHOICE" == "2" ]; then
    echo "🛠️ Opening cfdisk. Please create at least an EFI partition and a Linux Root partition."
    sleep 3
    cfdisk "$DISK"

    echo "Available partitions:"
    lsblk -p -n -l -o NAME,SIZE,TYPE "$DISK" | grep "part"
    
    echo -n "👉 Enter your EFI partition (e.g. /dev/sda1 or /dev/nvme0n1p1): "
    read PART_EFI
    echo -n "👉 Enter your Root partition (e.g. /dev/sda2 or /dev/nvme0n1p2): "
    read PART_ROOT

    if [ ! -b "$PART_EFI" ] || [ ! -b "$PART_ROOT" ]; then
        echo "❌ Error: Invalid partitions selected!"
        exit 1
    fi

    echo -n "⚠️ Do you want to format the EFI partition? (Type 'yes' for new installs, 'no' if you are sharing it with Windows): "
    read FORMAT_EFI
    if [ "$FORMAT_EFI" == "yes" ]; then
        mkfs.fat -F32 "$PART_EFI"
    fi
    
    echo "🔄 Formatting Root partition..."
    mkfs.ext4 -F "$PART_ROOT"
else
    echo "❌ Invalid choice."
    exit 1
fi

# Mount partitions
echo "🔄 Mounting partitions..."
mount "$PART_ROOT" /mnt
mkdir -p /mnt/boot/efi
mount "$PART_EFI" /mnt/boot/efi

# Optimize pacman download speed on the Live ISO
sed -i 's/^#ParallelDownloads = 5/ParallelDownloads = 5/' /etc/pacman.conf

# Install base system
echo "📥 Installing base Arch Linux system..."
pacstrap /mnt base base-devel linux linux-firmware nano git networkmanager wpa_supplicant sudo grub efibootmgr ufw os-prober

# Generate fstab
echo "⚙️ Generating fstab..."
genfstab -U /mnt >> /mnt/etc/fstab

# Prepare Post-Install inside chroot
echo "📥 Fetching post-install script..."
CURRENT_STEP="Fetching post-install script"
# If run via 'curl | bash', $0 is 'bash' and there's no local directory.
# In that case, clone the repo to get post-install.sh.
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -z "$SCRIPT_DIR" ] || [ ! -f "$SCRIPT_DIR/post-install.sh" ]; then
    echo "    Downloading NooreldeanOS installer files..."
    git clone --depth 1 https://github.com/coach-nooreldean/NooreldeanOS-Dotfiles.git /tmp/NooreldeanOS-Dotfiles
    SCRIPT_DIR="/tmp/NooreldeanOS-Dotfiles"
fi
cp "$SCRIPT_DIR/post-install.sh" /mnt/post-install.sh
chmod +x /mnt/post-install.sh

# Chroot and execute post-install
CURRENT_STEP="Chroot and post-install"
echo "🚀 Chrooting into the new system to complete installation..."
arch-chroot /mnt /post-install.sh "$DISK"

# Clean up
echo "🧹 Cleaning up..."
rm -f /mnt/post-install.sh
umount -R /mnt

echo "✅ NooreldeanOS installed successfully! You can now type 'reboot'."
