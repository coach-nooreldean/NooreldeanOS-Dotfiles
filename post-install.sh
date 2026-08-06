#!/bin/bash
# Post-Install Script for NooreldeanOS (Runs inside arch-chroot)
set -eo pipefail

# Repository URL for dotfiles
# We try to get the dynamic git URL if cloned, otherwise fallback to the default.
REPO_URL=$(git config --get remote.origin.url 2>/dev/null || echo "https://github.com/coach-nooreldean/NooreldeanOS-Dotfiles.git")

# Safety net: always clean up the temporary passwordless sudo override on exit,
# even if the script crashes or is interrupted mid-way.
# ⚠️ Note: If a sudden complete power loss occurs exactly here, the user might
# need to remove /etc/sudoers.d/99-temp-nopasswd manually from a live USB.
trap 'rm -f /etc/sudoers.d/99-temp-nopasswd' EXIT

DISK=$1
if [ -z "$DISK" ]; then
    echo "❌ Error: Disk argument missing for post-install."
    exit 1
fi

echo "🌍 Setting Timezone and Locale..."
echo "Available timezones examples: Africa/Cairo, America/New_York, Europe/London, Asia/Dubai, Asia/Riyadh"
echo "    (Full list: run 'timedatectl list-timezones' in another terminal)"
read -p "👉 Enter your timezone [Africa/Cairo]: " USER_TIMEZONE
USER_TIMEZONE=${USER_TIMEZONE:-Africa/Cairo}

if [ ! -f "/usr/share/zoneinfo/$USER_TIMEZONE" ]; then
    echo "⚠️ Invalid timezone '$USER_TIMEZONE'. Falling back to Africa/Cairo."
    USER_TIMEZONE="Africa/Cairo"
fi

ln -sf /usr/share/zoneinfo/$USER_TIMEZONE /etc/localtime
hwclock --systohc

sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

echo "🖥️ Setting Hostname..."
read -p "👉 Enter hostname for this machine [nooreldeanos]: " HOSTNAME
HOSTNAME=${HOSTNAME:-nooreldeanos}
echo "$HOSTNAME" > /etc/hostname
cat <<EOF > /etc/hosts
127.0.0.1   localhost
::1         localhost
127.0.1.1   ${HOSTNAME}.localdomain ${HOSTNAME}
EOF

echo "🌐 Enabling NetworkManager..."
mkdir -p /etc/NetworkManager/conf.d
echo -e "[device]\nwifi.backend=iwd" > /etc/NetworkManager/conf.d/iwd.conf
systemctl enable NetworkManager

echo "🔐 Configuring Users..."
read -p "👉 Enter username for the new user [nooreldean]: " USERNAME
USERNAME=${USERNAME:-nooreldean}

# Validate username (lowercase, no spaces, starts with letter)
if ! [[ "$USERNAME" =~ ^[a-z][a-z0-9_-]*$ ]]; then
    echo "❌ Invalid username '$USERNAME'. Must start with a lowercase letter and contain only a-z, 0-9, _, -"
    exit 1
fi

echo "🔑 Setting password for user '$USERNAME'..."
while true; do
    read -sp "Enter password for '$USERNAME': " USER_PASSWORD
    echo
    read -sp "Confirm password: " USER_PASSWORD_CONFIRM
    echo
    if [ "$USER_PASSWORD" == "$USER_PASSWORD_CONFIRM" ]; then
        break
    fi
    echo "❌ Passwords do not match! Please try again."
done

if ! id "$USERNAME" &>/dev/null; then
    useradd -m -G wheel -s /bin/bash "$USERNAME"
fi
printf "%s:%s\n" "$USERNAME" "$USER_PASSWORD" | chpasswd

echo "🔑 Setting root password..."
echo "Tip: Leave empty to disable the root account and rely purely on 'sudo' (Recommended)."
read -sp "Enter root password (or press Enter to disable root): " ROOT_PASSWORD
echo
if [ -z "$ROOT_PASSWORD" ]; then
    echo "Root account will be disabled."
    passwd -l root
else
    printf "%s:%s\n" "root" "$ROOT_PASSWORD" | chpasswd
fi

# Clear password variables from memory
unset USER_PASSWORD USER_PASSWORD_CONFIRM ROOT_PASSWORD

# Optimize pacman download speed on the new system
cp /etc/pacman.conf /etc/pacman.conf.bak
sed -i 's/^#ParallelDownloads/ParallelDownloads/' /etc/pacman.conf
grep -q "^ParallelDownloads" /etc/pacman.conf || echo "ParallelDownloads = 5" >> /etc/pacman.conf

sed -i 's/^#Color/Color/' /etc/pacman.conf
grep -q "^Color" /etc/pacman.conf || echo "Color" >> /etc/pacman.conf

# Enable 32-bit support (multilib) for apps like Steam or Wine
sed -i '/^#\[multilib\]/,/^#Include = \/etc\/pacman.d\/mirrorlist/ s/^#//' /etc/pacman.conf
pacman -Sy

# Optimize makepkg to use all available CPU cores minus one for insanely fast AUR compilation without freezing
cp /etc/makepkg.conf /etc/makepkg.conf.bak
sed -i "s/^#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j\$(( \$(nproc) > 1 ? \$(nproc) - 1 : 1 ))\"/" /etc/makepkg.conf

# Temporarily allow wheel group to use sudo WITHOUT password (for automated yay and install.sh)
# Using sudoers.d drop-in file instead of editing /etc/sudoers directly (safer)
echo "%wheel ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/99-temp-nopasswd
chmod 440 /etc/sudoers.d/99-temp-nopasswd

echo "🔍 Detecting CPU and installing Microcode..."
CPU_VENDOR=$(lscpu | grep "Vendor ID" | awk '{print $3}')
if [[ "$CPU_VENDOR" == *"Intel"* ]]; then
    pacman -S --noconfirm intel-ucode
elif [[ "$CPU_VENDOR" == *"AMD"* ]]; then
    pacman -S --noconfirm amd-ucode
fi

echo "🎮 Detecting GPU and installing drivers..."
if lspci | grep -i "vga.*nvidia\|3d.*nvidia" &> /dev/null; then
    echo "Nvidia GPU detected! Installing proprietary drivers..."
    pacman -S --noconfirm nvidia nvidia-utils
    # Hyprland requires nvidia-drm.modeset=1 for Nvidia cards and Early KMS modules
    sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvidia-drm.modeset=1 /' /etc/default/grub
    sed -i 's/^MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf
    mkinitcpio -P
    
    # Check for Optimus (Dual GPU) setups
    if lspci | grep -i "vga.*intel\|vga.*amd" &> /dev/null; then
        echo -e "\n⚠️  WARNING: Multiple GPUs detected (e.g., Optimus Laptop). "
        echo "If you experience a black screen in Hyprland, you may need to set WLR_NO_HARDWARE_CURSORS=1"
        echo -e "or configure env variables in ~/.config/hypr/hyprland.conf.\n"
        sleep 3
    fi
fi

echo "👢 Installing GRUB Bootloader..."
# Enable os-prober for Windows Dual-Boot detection
echo "GRUB_DISABLE_OS_PROBER=false" >> /etc/default/grub
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
echo "💡 Tip: If you are dual-booting Windows, it may not be detected right now."
echo "   After you boot into your new system, mount your Windows partition and run:"
echo "   sudo grub-mkconfig -o /boot/grub/grub.cfg"

echo "📥 Setting up NooreldeanOS Dotfiles..."
# Switch to the created user to clone and install dotfiles
su - "$USERNAME" -c "
    export AUTO_INSTALL=1
    echo 'Cloning Dotfiles repository...'
    git clone \"$REPO_URL\" ~/NooreldeanOS-Dotfiles
    cd ~/NooreldeanOS-Dotfiles
    echo 'Running NooreldeanOS install.sh...'
    bash install.sh
"

# Remove temporary sudoers override and enable password-required sudo
rm -f /etc/sudoers.d/99-temp-nopasswd
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/wheel
chmod 440 /etc/sudoers.d/wheel

echo "✅ Post-installation setup complete!"
