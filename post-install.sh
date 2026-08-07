#!/bin/bash
# Post-Install Script for NooreldeanOS (Runs inside arch-chroot)
set -eo pipefail

# Source configuration and logger
# shellcheck source=/dev/null
source "/lib/config.conf"
# shellcheck source=/dev/null
source "/lib/logger.sh"

# Repository URL for dotfiles
# We try to get the dynamic git URL if cloned, otherwise fallback to the default.
REPO_URL=$(git config --get remote.origin.url 2>/dev/null || echo "https://github.com/coach-nooreldean/NooreldeanOS-Dotfiles.git")

# Safety net: always clean up the temporary passwordless sudo override on exit
trap 'rm -f /etc/sudoers.d/99-temp-nopasswd' EXIT

DISK=$1
if [ -z "$DISK" ]; then
    log_error "Disk argument missing for post-install."
    exit 1
fi

log_step "Setting Timezone and Locale..."
log_info "Available timezones examples: Africa/Cairo, America/New_York, Europe/London, Asia/Dubai, Asia/Riyadh"
log_prompt "Enter your timezone [${DEFAULT_TIMEZONE}]: "
read -r USER_TIMEZONE
USER_TIMEZONE=${USER_TIMEZONE:-$DEFAULT_TIMEZONE}

if [ ! -f "/usr/share/zoneinfo/$USER_TIMEZONE" ]; then
    log_warning "Invalid timezone '$USER_TIMEZONE'. Falling back to ${DEFAULT_TIMEZONE}."
    USER_TIMEZONE="$DEFAULT_TIMEZONE"
fi

ln -sf "/usr/share/zoneinfo/$USER_TIMEZONE" /etc/localtime
hwclock --systohc

sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

log_step "Setting Hostname..."
log_prompt "Enter hostname for this machine [${DEFAULT_HOSTNAME}]: "
read -r HOSTNAME
HOSTNAME=${HOSTNAME:-$DEFAULT_HOSTNAME}
echo "$HOSTNAME" > /etc/hostname
cat <<EOF > /etc/hosts
127.0.0.1   localhost
::1         localhost
127.0.1.1   ${HOSTNAME}.localdomain ${HOSTNAME}
EOF

log_step "Enabling NetworkManager..."
mkdir -p /etc/NetworkManager/conf.d
echo -e "[device]\nwifi.backend=iwd" > /etc/NetworkManager/conf.d/iwd.conf
systemctl enable NetworkManager

log_step "Configuring Users..."
log_prompt "Enter username for the new user [${DEFAULT_USERNAME}]: "
read -r USERNAME
USERNAME=${USERNAME:-$DEFAULT_USERNAME}

# Validate username (lowercase, no spaces, starts with letter)
if ! [[ "$USERNAME" =~ ^[a-z][a-z0-9_-]*$ ]]; then
    log_error "Invalid username '$USERNAME'. Must start with a lowercase letter and contain only a-z, 0-9, _, -"
    exit 1
fi

log_info "Setting password for user '$USERNAME'..."
while true; do
    log_prompt "Enter password for '$USERNAME': "
    read -r -s USER_PASSWORD
    echo
    log_prompt "Confirm password: "
    read -r -s USER_PASSWORD_CONFIRM
    echo
    if [ "$USER_PASSWORD" == "$USER_PASSWORD_CONFIRM" ]; then
        break
    fi
    log_error "Passwords do not match! Please try again."
done

if ! id "$USERNAME" &>/dev/null; then
    useradd -m -G wheel -s /bin/bash "$USERNAME"
fi
printf "%s:%s\n" "$USERNAME" "$USER_PASSWORD" | chpasswd

log_info "Setting root password..."
log_info "Tip: Leave empty to disable the root account and rely purely on 'sudo' (Recommended)."
log_prompt "Enter root password (or press Enter to disable root): "
read -r -s ROOT_PASSWORD
echo
if [ -z "$ROOT_PASSWORD" ]; then
    log_info "Root account will be disabled."
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
sed -i 's/^# %wheel ALL=(ALL:ALL) NOPASSWD: ALL/%wheel ALL=(ALL:ALL) NOPASSWD: ALL/' /etc/sudoers


log_step "Detecting CPU and installing Microcode..."
CPU_VENDOR=$(lscpu | grep "Vendor ID" | awk '{print $3}')
if [[ "$CPU_VENDOR" == *"Intel"* ]]; then
    pacman -S --noconfirm intel-ucode
elif [[ "$CPU_VENDOR" == *"AMD"* ]]; then
    pacman -S --noconfirm amd-ucode
fi

log_step "Detecting GPU and installing drivers..."
if lspci | grep -i "vga.*nvidia\|3d.*nvidia" &> /dev/null; then
    log_info "Nvidia GPU detected! Installing proprietary drivers..."
    pacman -S --noconfirm nvidia nvidia-utils
    # Hyprland requires nvidia-drm.modeset=1 for Nvidia cards and Early KMS modules
    sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvidia-drm.modeset=1 /' /etc/default/grub
    sed -i 's/^MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf
    mkinitcpio -P
    
    # Check for Optimus (Dual GPU) setups
    if lspci | grep -i "vga.*intel\|vga.*amd" &> /dev/null; then
        log_warning "Multiple GPUs detected (e.g., Optimus Laptop). "
        log_warning "If you experience a black screen in Hyprland, you may need to set WLR_NO_HARDWARE_CURSORS=1"
        log_warning "or configure env variables in ~/.config/hypr/hyprland.conf."
        sleep 3
    fi
elif lspci | grep -i "vga.*amd\|3d.*amd" &> /dev/null; then
    log_info "AMD GPU detected! Configuring Early KMS to prevent black screens..."
    pacman -S --noconfirm vulkan-radeon libva-mesa-driver mesa-vdpau
    sed -i 's/^MODULES=()/MODULES=(amdgpu)/' /etc/mkinitcpio.conf
    mkinitcpio -P
elif lspci | grep -i "vga.*intel\|3d.*intel" &> /dev/null; then
    log_info "Intel GPU detected! Configuring Early KMS to prevent black screens..."
    pacman -S --noconfirm vulkan-intel intel-media-driver
    sed -i 's/^MODULES=()/MODULES=(i915)/' /etc/mkinitcpio.conf
    mkinitcpio -P
fi

log_step "Installing GRUB Bootloader..."
# Enable os-prober for Windows Dual-Boot detection
echo "GRUB_DISABLE_OS_PROBER=false" >> /etc/default/grub
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
log_info "Tip: If you are dual-booting Windows, it may not be detected right now."
log_info "   After you boot into your new system, mount your Windows partition and run:"
log_info "   sudo grub-mkconfig -o /boot/grub/grub.cfg"

log_step "Setting up NooreldeanOS Dotfiles..."
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
sed -i 's/^%wheel ALL=(ALL:ALL) NOPASSWD: ALL/# %wheel ALL=(ALL:ALL) NOPASSWD: ALL/' /etc/sudoers
sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

log_success "Post-installation setup complete!"
