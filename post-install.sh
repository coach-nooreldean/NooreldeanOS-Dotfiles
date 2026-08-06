#!/bin/bash
# Post-Install Script for NooreldeanOS (Runs inside arch-chroot)
set -e

DISK=$1
if [ -z "$DISK" ]; then
    echo "❌ Error: Disk argument missing for post-install."
    exit 1
fi

echo "🌍 Setting Timezone and Locale..."
ln -sf /usr/share/zoneinfo/Africa/Cairo /etc/localtime
hwclock --systohc

sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

echo "🖥️ Setting Hostname..."
echo "nooreldeanos" > /etc/hostname
cat <<EOF > /etc/hosts
127.0.0.1   localhost
::1         localhost
127.0.1.1   nooreldeanos.localdomain nooreldeanos
EOF

echo "🌐 Enabling NetworkManager..."
systemctl enable NetworkManager

echo "🔐 Configuring Users..."
# Prompt for root password (or set a default one and prompt user to change later, but interactive is better)
# Since we are automating, let's ask for the user password now
echo "Enter password for the new user 'nooreldean': "
read -s USER_PASSWORD
echo "Confirm password: "
read -s USER_PASSWORD_CONFIRM

if [ "$USER_PASSWORD" != "$USER_PASSWORD_CONFIRM" ]; then
    echo "❌ Passwords do not match! Setting default password to '1234'. PLEASE CHANGE IT LATER."
    USER_PASSWORD="1234"
fi

useradd -m -G wheel -s /bin/bash nooreldean
echo "nooreldean:$USER_PASSWORD" | chpasswd
echo "root:$USER_PASSWORD" | chpasswd

# Optimize pacman download speed on the new system
sed -i 's/^#ParallelDownloads = 5/ParallelDownloads = 5/' /etc/pacman.conf
sed -i 's/^#Color/Color/' /etc/pacman.conf

# Enable 32-bit support (multilib) for apps like Steam or Wine
sed -i '/^#\[multilib\]/,/^#Include = \/etc\/pacman.d\/mirrorlist/ s/^#//' /etc/pacman.conf

# Optimize makepkg to use all CPU cores for insanely fast AUR compilation
sed -i "s/^#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j\$(nproc)\"/" /etc/makepkg.conf

# Temporarily allow wheel group to use sudo WITHOUT password (for automated yay install)
sed -i 's/^# %wheel ALL=(ALL:ALL) NOPASSWD: ALL/%wheel ALL=(ALL:ALL) NOPASSWD: ALL/' /etc/sudoers

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
# Switch to user nooreldean to clone and install dotfiles
su - nooreldean -c "
    echo 'Cloning Dotfiles repository...'
    git clone https://github.com/coach-nooreldean/NooreldeanOS-Dotfiles.git ~/NooreldeanOS-Dotfiles
    cd ~/NooreldeanOS-Dotfiles
    echo 'Running NooreldeanOS install.sh...'
    bash install.sh
"

# Revert sudoers to require password for security
sed -i 's/^%wheel ALL=(ALL:ALL) NOPASSWD: ALL/# %wheel ALL=(ALL:ALL) NOPASSWD: ALL/' /etc/sudoers
sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

echo "✅ Post-installation setup complete!"
