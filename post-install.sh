#!/bin/bash
# Post-Install Script for NooreldeanOS (Runs inside arch-chroot)
set -e

# Safety net: always clean up the temporary passwordless sudo override on exit,
# even if the script crashes or is interrupted mid-way.
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

useradd -m -G wheel -s /bin/bash "$USERNAME"
chpasswd <<< "$USERNAME:$USER_PASSWORD"

echo "🔑 Setting root password (leave empty to use same as user)..."
read -sp "Enter root password [same as user]: " ROOT_PASSWORD
echo
if [ -z "$ROOT_PASSWORD" ]; then
    ROOT_PASSWORD="$USER_PASSWORD"
fi
chpasswd <<< "root:$ROOT_PASSWORD"

# Clear password variables from memory
unset USER_PASSWORD USER_PASSWORD_CONFIRM ROOT_PASSWORD

# Optimize pacman download speed on the new system
sed -i 's/^#ParallelDownloads = 5/ParallelDownloads = 5/' /etc/pacman.conf
sed -i 's/^#Color/Color/' /etc/pacman.conf

# Enable 32-bit support (multilib) for apps like Steam or Wine
sed -i '/^#\[multilib\]/,/^#Include = \/etc\/pacman.d\/mirrorlist/ s/^#//' /etc/pacman.conf

# Optimize makepkg to use all CPU cores for insanely fast AUR compilation
sed -i "s/^#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j\$(nproc)\"/" /etc/makepkg.conf

# Temporarily allow wheel group to use sudo WITHOUT password (for automated yay install)
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
    # Hyprland requires nvidia-drm.modeset=1 for Nvidia cards
    sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvidia-drm.modeset=1 /' /etc/default/grub
fi

echo "👢 Installing GRUB Bootloader..."
# Enable os-prober for Windows Dual-Boot detection
echo "GRUB_DISABLE_OS_PROBER=false" >> /etc/default/grub
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg

echo "📥 Setting up NooreldeanOS Dotfiles..."
# Switch to the created user to clone and install dotfiles
su - "$USERNAME" -c "
    echo 'Cloning Dotfiles repository...'
    git clone https://github.com/coach-nooreldean/NooreldeanOS-Dotfiles.git ~/NooreldeanOS-Dotfiles
    cd ~/NooreldeanOS-Dotfiles
    echo 'Running NooreldeanOS install.sh...'
    bash install.sh
"

# Remove temporary sudoers override and enable password-required sudo
rm -f /etc/sudoers.d/99-temp-nopasswd
sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

echo "✅ Post-installation setup complete!"
