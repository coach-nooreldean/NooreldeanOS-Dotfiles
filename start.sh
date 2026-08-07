#!/bin/bash
# NooreldeanOS Arch Linux Automatic Installer
set -eo pipefail

# Repository URL for dotfiles
# We try to get the dynamic git URL if cloned, otherwise fallback to the default.
REPO_URL=$(git config --get remote.origin.url 2>/dev/null || echo "https://github.com/coach-nooreldean/NooreldeanOS-Dotfiles.git")

# Error handler: show which step failed before exiting
CURRENT_STEP="Initialization"
trap 'echo -e "\n❌ ERROR: Installation failed at step: $CURRENT_STEP (line $LINENO)"; echo "   Check the output above for details."' ERR

echo "🚀 Welcome to the NooreldeanOS Automatic Installer!"
echo "⚠️ WARNING: This will ERASE EVERYTHING on the selected disk."

# Clean up any leftover temp sudoers from a previous interrupted run (e.g. from a chroot attempt)
umount -R /mnt 2>/dev/null || true
swapoff -a 2>/dev/null || true
rm -f /mnt/etc/sudoers.d/99-temp-nopasswd 2>/dev/null || true

# Pre-flight checks
if [ ! -d /sys/firmware/efi ]; then
    echo "❌ Error: System is NOT booted in UEFI mode!"
    echo "   NooreldeanOS requires UEFI. Please reboot in UEFI mode."
    exit 1
fi
if ! mountpoint -q /sys/firmware/efi/efivars; then
    echo "❌ Error: efivarfs is not mounted! GRUB installation will fail."
    echo "   Please reboot or mount it manually."
    exit 1
fi

if ! ping -c 1 -W 3 1.1.1.1 &> /dev/null && ! curl -Is --connect-timeout 3 https://archlinux.org &> /dev/null; then
    echo "❌ Error: No internet connection detected!"
    echo "   Please connect to the internet first (use 'iwctl' for WiFi)."
    exit 1
fi

# List available disks
echo "Available disks:"
mapfile -t DISKS < <(lsblk -d -p -n -l -o NAME,SIZE,MODEL | grep -E '/dev/sd|/dev/nvme|/dev/vd')

if [ ${#DISKS[@]} -eq 0 ]; then
    echo "❌ Error: No disks found!"
    exit 1
fi

for i in "${!DISKS[@]}"; do
    echo "$((i+1))) ${DISKS[$i]}"
done

while true; do
    echo -n "👉 Select the disk number to install on (1-${#DISKS[@]}): "
    read -r DISK_NUM

    if [[ "$DISK_NUM" =~ ^[0-9]+$ ]] && [ "$DISK_NUM" -ge 1 ] && [ "$DISK_NUM" -le "${#DISKS[@]}" ]; then
        break
    else
        echo "❌ Error: Invalid selection! Please try again."
    fi
done

DISK_INFO="${DISKS[$((DISK_NUM-1))]}"
DISK=$(echo "$DISK_INFO" | awk '{print $1}')
echo "✅ Selected disk: $DISK_INFO"

if [ ! -b "$DISK" ]; then
    echo "❌ Error: Disk $DISK is not a valid block device!"
    exit 1
fi

echo "💽 Choose Root Filesystem:"
echo "1) ext4 (Classic & High Stability - Default)"
echo "2) btrfs (Modern with Subvolumes '@' & '@home' for Snapshots)"
read -r -p "Choice [1/2]: " FS_CHOICE
FS_CHOICE=${FS_CHOICE:-1}

echo "⚙️ Choose Partitioning Method:"
echo "1) 🧹 Auto-Wipe & Partition (ERASES ENTIRE DISK - 1GB EFI, Rest Root)"
echo "2) 🛠️ Manual Partitioning (Opens cfdisk to create partitions manually)"
read -r -p "Choice [1/2]: " PART_CHOICE

if [ "$PART_CHOICE" == "1" ]; then
    # Sanity check: Ensure disk is at least 15GB
    DISK_SIZE_BYTES=$(lsblk -b -d -n -o SIZE "$DISK" 2>/dev/null || echo 0)
    if [ "$DISK_SIZE_BYTES" -lt 15000000000 ]; then
        echo "❌ Error: Disk $DISK is too small (less than 15GB). Arch Linux requires more space."
        exit 1
    fi

    echo "⚠️ Existing partitions on $DISK_INFO:"
    lsblk -p -n -l -o NAME,SIZE,TYPE,MOUNTPOINT "$DISK" | grep "part" || echo "   (No existing partitions found)"
    echo -e "\e[31m⚠️ WARNING: You are about to ERASE ALL DATA on $DISK_INFO.\e[0m"
    read -r -p "    Type '$DISK' to confirm: " CONFIRM
    if [ "$CONFIRM" != "$DISK" ]; then
        echo "Aborted."
        exit 1
    fi

    echo "🔄 Wiping and partitioning $DISK..."
    for part in $(lsblk -p -n -l -o NAME "$DISK" | grep "part"); do
        umount "$part" 2>/dev/null || true
    done
    # Zero out the beginning of the disk to destroy stubborn metadata/GPT tables
    dd if=/dev/zero of="$DISK" bs=1M count=100 status=none
    wipefs -af "$DISK"
    sgdisk -Z "$DISK"
    sgdisk -n 1:0:+1G -t 1:ef00 -c 1:"EFI System" "$DISK"
    sgdisk -n 2:0:0 -t 2:8300 -c 2:"Linux Root" "$DISK"
    partprobe "$DISK"
    sleep 2

    if [ -b "${DISK}p1" ]; then
        PART_EFI="${DISK}p1"
        PART_ROOT="${DISK}p2"
    else
        PART_EFI="${DISK}1"
        PART_ROOT="${DISK}2"
    fi

    echo "🔄 Formatting partitions..."
    umount "$PART_EFI" 2>/dev/null || true
    umount "$PART_ROOT" 2>/dev/null || true
    mkfs.fat -F32 "$PART_EFI"
    if [ "$FS_CHOICE" == "2" ]; then
        mkfs.btrfs -f "$PART_ROOT"
    else
        mkfs.ext4 -F "$PART_ROOT"
    fi
    
elif [ "$PART_CHOICE" == "2" ]; then
    echo "🛠️ Opening cfdisk. Please create at least an EFI partition and a Linux Root partition."
    sleep 3
    cfdisk "$DISK"

    echo "Available partitions:"
    mapfile -t PARTS < <(lsblk -p -n -l -o NAME,SIZE,TYPE "$DISK" | grep "part")
    
    if [ ${#PARTS[@]} -eq 0 ]; then
        echo "❌ Error: No partitions found on $DISK!"
        exit 1
    fi

    for i in "${!PARTS[@]}"; do
        echo "$((i+1))) ${PARTS[$i]}"
    done
    
    while true; do
        echo -n "👉 Enter the number of your EFI partition (1-${#PARTS[@]}): "
        read -r EFI_NUM
        echo -n "👉 Enter the number of your Root partition (1-${#PARTS[@]}): "
        read -r ROOT_NUM

        if [[ "$EFI_NUM" =~ ^[0-9]+$ ]] && [ "$EFI_NUM" -ge 1 ] && [ "$EFI_NUM" -le "${#PARTS[@]}" ] && \
           [[ "$ROOT_NUM" =~ ^[0-9]+$ ]] && [ "$ROOT_NUM" -ge 1 ] && [ "$ROOT_NUM" -le "${#PARTS[@]}" ]; then
            break
        else
            echo "❌ Error: Invalid partition selection! Please try again."
        fi
    done

    PART_EFI=$(echo "${PARTS[$((EFI_NUM-1))]}" | awk '{print $1}')
    PART_ROOT=$(echo "${PARTS[$((ROOT_NUM-1))]}" | awk '{print $1}')
    
    echo "✅ Selected EFI: $PART_EFI"
    echo "✅ Selected Root: $PART_ROOT"

    read -r -p "⚠️ Are you ABSOLUTELY SURE these are the correct partitions? (Type 'yes' to confirm): " CONFIRM_MANUAL
    if [ "$CONFIRM_MANUAL" != "yes" ]; then
        echo "❌ Aborting installation. Please run the script again and select carefully."
        exit 1
    fi

    echo -n "⚠️ Do you want to format the EFI partition? (Type 'yes' for new installs, 'no' if you are sharing it with Windows): "
    read -r FORMAT_EFI
    if [ "$FORMAT_EFI" == "yes" ]; then
        umount "$PART_EFI" 2>/dev/null || true
        mkfs.fat -F32 "$PART_EFI"
    fi
    
    echo "🔄 Formatting Root partition..."
    umount "$PART_ROOT" 2>/dev/null || true
    if [ "$FS_CHOICE" == "2" ]; then
        mkfs.btrfs -f "$PART_ROOT"
    else
        mkfs.ext4 -F "$PART_ROOT"
    fi
else
    echo "❌ Invalid choice."
    exit 1
fi

# Mount partitions
echo "🔄 Mounting partitions..."
if [ "$FS_CHOICE" == "2" ]; then
    mount "$PART_ROOT" /mnt
    btrfs subvolume create /mnt/@
    btrfs subvolume create /mnt/@home
    btrfs subvolume create /mnt/@log
    btrfs subvolume create /mnt/@cache
    btrfs subvolume create /mnt/@swap
    umount /mnt

    BTRFS_OPTS="noatime,compress=zstd,space_cache=v2,discard=async"
    mount -o "$BTRFS_OPTS,subvol=@" "$PART_ROOT" /mnt
    mkdir -p /mnt/home /mnt/boot/efi /mnt/var/log /mnt/var/cache /mnt/swap
    mount -o "$BTRFS_OPTS,subvol=@home" "$PART_ROOT" /mnt/home
    mount -o "$BTRFS_OPTS,subvol=@log" "$PART_ROOT" /mnt/var/log
    mount -o "$BTRFS_OPTS,subvol=@cache" "$PART_ROOT" /mnt/var/cache
    mount -o "noatime,space_cache=v2,discard=async,subvol=@swap" "$PART_ROOT" /mnt/swap
    mount "$PART_EFI" /mnt/boot/efi
else
    mount "$PART_ROOT" /mnt
    mkdir -p /mnt/boot/efi
    mount "$PART_EFI" /mnt/boot/efi
fi

# Optimize pacman download speed on the Live ISO
cp /etc/pacman.conf /etc/pacman.conf.bak
sed -i 's/^#ParallelDownloads/ParallelDownloads/' /etc/pacman.conf
grep -q "^ParallelDownloads" /etc/pacman.conf || echo "ParallelDownloads = 5" >> /etc/pacman.conf

echo "🔍 Optimizing mirrorlist with reflector (This may take a minute)..."
reflector --latest 10 --sort rate --save /etc/pacman.d/mirrorlist || echo "⚠️ Warning: Reflector failed, using default mirrors."

# Install base system
echo "📥 Installing base Arch Linux system..."
EXTRA_PKGS=""
if [ "$FS_CHOICE" == "2" ]; then
    EXTRA_PKGS="btrfs-progs"
fi
pacstrap /mnt base base-devel linux linux-firmware nano git networkmanager iwd sudo grub efibootmgr ufw os-prober pciutils $EXTRA_PKGS

# Generate fstab
echo "⚙️ Generating fstab..."
genfstab -U /mnt >> /mnt/etc/fstab

# Optional Swapfile Creation
echo "💡 Do you want to create a Swapfile?"
echo "   (Note: NooreldeanOS uses ZRAM automatically, so you only need a Swapfile if you plan to use Hibernation or have very low RAM)"
read -r -p "    Create Swapfile? [y/N]: " CREATE_SWAP
if [[ "$CREATE_SWAP" =~ ^[Yy]$ ]]; then
    read -r -p "    👉 Enter Swapfile size in GB (e.g., 8): " SWAP_SIZE
    if [[ "$SWAP_SIZE" =~ ^[0-9]+$ ]]; then
        echo "🔄 Creating ${SWAP_SIZE}GB Swapfile..."
        if [ "$FS_CHOICE" == "2" ]; then
            # BTRFS Swapfile (Requires btrfs-progs)
            btrfs filesystem mkswapfile --size "${SWAP_SIZE}g" --uuid clear /mnt/swap/swapfile || echo "⚠️ Failed to create Btrfs swapfile."
            echo "/swap/swapfile none swap defaults 0 0" >> /mnt/etc/fstab
            echo "💡 Tip: To use Hibernation on BTRFS, you must calculate the resume_offset of this swapfile"
            echo "   and add 'resume=/dev/mapper/YOUR_PARTITION resume_offset=OFFSET' to your GRUB config."
        else
            # EXT4 Swapfile
            dd if=/dev/zero of=/mnt/swapfile bs=1M count=$((SWAP_SIZE * 1024)) status=progress
            chmod 600 /mnt/swapfile
            mkswap /mnt/swapfile
            echo "/swapfile none swap defaults 0 0" >> /mnt/etc/fstab
        fi
        echo "✅ Swapfile created and added to fstab."
    else
        echo "⚠️ Invalid size. Skipping Swapfile creation."
    fi
fi

# Prepare Post-Install inside chroot
echo "📥 Fetching post-install script..."
CURRENT_STEP="Fetching post-install script"

# If run via 'curl | bash', $0 is 'bash' and there's no local directory.
# In that case, clone the repo to get post-install.sh.
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -z "$SCRIPT_DIR" ] || [ ! -f "$SCRIPT_DIR/post-install.sh" ]; then
    echo "    Downloading NooreldeanOS installer files..."
    if ! command -v git &> /dev/null; then
        echo "    Git not found, installing on live environment..."
        pacman -Sy --noconfirm git || true
    fi
    git clone --depth 1 "$REPO_URL" /tmp/NooreldeanOS-Dotfiles
    SCRIPT_DIR="/tmp/NooreldeanOS-Dotfiles"
fi
cp -r "$SCRIPT_DIR/lib" /mnt/lib
cp "$SCRIPT_DIR/post-install.sh" /mnt/post-install.sh
chmod +x /mnt/post-install.sh

# Chroot and execute post-install
CURRENT_STEP="Chroot and post-install"
echo "🚀 Chrooting into the new system to complete installation..."
arch-chroot /mnt /post-install.sh "$DISK"

# Clean up
echo "🧹 Cleaning up..."
rm -f /mnt/post-install.sh
rm -rf /mnt/lib
rm -f /mnt/etc/sudoers.d/99-temp-nopasswd
umount -R /mnt

echo "✅ NooreldeanOS installed successfully! You can now type 'reboot'."
