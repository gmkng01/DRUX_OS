#!/bin/bash

# set -e  # Exit on error
# set -o pipefail

# sudo pacman -S --needed base-devel

# echo "==> Updating mirror list..."
# cd mirror && ./get_mirror.sh && cd ~

# # List of packages from official repos
# programs=(
#     qtile neovim git htop curl wget firefox polkit-gnome terminator rofi picom
#     font-manager blueman bluez bluez-utils  pavucontrol
#     brightnessctl pamixer 
#     xarchiver zip unzip unrar p7zip python-dbus-next mtpfs gvfs-mtp gvfs-gphoto2
#     telegram-desktop lxappearance xfce4-screenshooter
#     upower sxiv mpv gnome-disk-utility kdeconnect pcmanfm python-pywayland
#     ripgrep xfce4-power-manager python-pyqt6 zenity fish xfce4-volumed-pulse gnome-keyring redshift
# )

# # List of AUR packages
# aur_programs=(
#     visual-studio-code-bin betterlockscreen dracula-gtk-theme-full dracula-icons-git
#     pfetch python-pulsectl jmtpfs python-colorthief
#     qtile-extras brightnessctl nitrogen trayer grub-customizer-git
# )

# install_programs() {
#     echo "==> Updating system..."
#     sudo pacman -Syu --noconfirm

#     echo "==> Installing official packages..."
#     for program in "${programs[@]}"; do
#         if pacman -Qi "$program" &>/dev/null; then
#             echo "✔ $program is already installed."
#         else
#             sudo pacman -S --noconfirm "$program"
#         fi
#     done
# }

# setup_yay() {
#     echo "==> Setting up yay AUR helper..."
#     mkdir -p ~/Sources
#     cd ~/Sources

#     if [ ! -d "yay" ]; then
#         git clone https://aur.archlinux.org/yay.git
#     else
#         echo "✔ yay already cloned."
#     fi

#     cd yay
#     makepkg -si --noconfirm
# }

# install_aur_programs() {
#     echo "==> Installing AUR packages..."
#     for aur_program in "${aur_programs[@]}"; do
#         yay -S --noconfirm "$aur_program"
#     done
# }

# copy_configs() {
#     echo "==> Setting up configuration files..."
#     cd ~/DRUX_OS

#     echo "📁 Copying fonts..."
#     sudo cp -rT fonts /usr/local/share/fonts/
#     sudo fc-cache -vf

#     echo "📁 Copying .config directory..."
#     cp -rT .config ~/.config/

#     echo "📄 Copying dotfiles..."
#     cp -T .bashrc ~/.bashrc
#     cp -T .xinitrc ~/.xinitrc
#     cp -T .Xmodmap ~/.Xmodmap
#     cp -T .zshrc ~/.zshrc

#     echo "🧠 Adding Xmodmap to xinitrc..."
#     XINITRC="/etc/X11/xinit/xinitrc"
#     LINE='xmodmap ~/.Xmodmap'
#     if ! grep -Fxq "$LINE" "$XINITRC"; then
#         echo "$LINE" | sudo tee -a "$XINITRC" > /dev/null
#         echo "✔ Added to $XINITRC"
#     else
#         echo "✔ Xmodmap line already exists in $XINITRC"
#     fi
# }

# copy_system_configs() {
#     echo "==> Copying system configuration files..."

#     sudo cp 50-libinput.conf /etc/X11/xorg.conf.d/
#     sudo cp 10-serverflags.conf /etc/X11/xorg.conf.d/
#     sudo cp 99-removable.rules /etc/udev/rules.d/
#     sudo cp -rT lightdm /etc/lightdm
#     sudo cp -rT grub /boot/grub/
#     sudo cp -rT walls/background.jpeg /usr/share/pixmaps/background.jpeg
# }

# enable_services() {
#     echo "==> Enabling services..."
#     sudo systemctl enable bluetooth
#     sudo systemctl start bluetooth
#     systemctl --user status trayer.service
#     systemctl --user status volctl.service
#     systemctl --user status wallpaper.service
#     systemctl --user status polkit.service
#     systemctl --user status picom.service
#     systemctl --user status nm-applet.service
#     systemctl --user status graphical-session.service
#     systemctl --user status blueman-applet.service
#     systemctl --user status battery-low.service
# }

# adding_starship_promt(){
#     echo "==> Installing Starship Prompt"
#     curl -sS https://starship.rs/install.sh | sh -s -- -y
# }

# change_shell_fish(){
#     echo "==> Changing shel Bash to Fish"
#     chsh -s "$(command -v fish)"
# }

# final_touches() {
#     echo "==> Final touches..."

#     git config --global user.name "Abhishek Mishra"
#     git config --global user.email "gmkng1@gmail.com"

#     mkdir -p ~/Pictures/Screenshots
#     cp -rT walls ~/Pictures/walls
# }

# main() {
#     install_programs
#     setup_yay
#     install_aur_programs
#     copy_configs
#     copy_system_configs
#     enable_services
#     adding_starship_promt
#     change_shell_fish
#     final_touches
#     echo "🎉 Installation complete!"

#     # Prompt for reboot
#     read -rp "🔁 Do you want to reboot now? (y/n): " answer
#     if [[ "$answer" =~ ^[Yy]$ ]]; then
#         echo "Rebooting system..."
#         sudo reboot
#     else
#         echo "Reboot skipped. Please reboot manually later to apply all changes."
#     fi
# }
# main




#!/usr/bin/env bash

set -euo pipefail  # Exit on error, unset vars, and pipe failures

# --- Configuration ---
REPOS_DIR="$HOME/DRUX_OS"
SOURCES_DIR="$HOME/Sources"

official_programs=(
    neovim git htop wget firefox polkit-gnome terminator rofi picom
    font-manager blueman bluez bluez-utils pavucontrol brightnessctl pamixer 
    xarchiver zip unzip unrar p7zip python-dbus-next mtpfs ntfs-3g gvfs-mtp gvfs-gphoto2
    lxappearance xfce4-screenshooter mpv gnome-disk-utility
    pcmanfm ripgrep python-pyqt6 zenity fish 
    gnome-keyring redshift feh
)

aur_programs=(
    visual-studio-code-bin betterlockscreen dracula-gtk-theme-full 
    dracula-icons-git pfetch jmtpfs python-colorthief
    qtile-extras trayer grub-customizer-git
)

# --- Functions ---

prep_system() {
    echo "==> Initializing System..."
    sudo pacman -S --needed --noconfirm base-devel git
}

install_official() {
    echo "==> Installing official packages..."
    sudo pacman -Syu --needed --noconfirm "${official_programs[@]}"
}

setup_yay() {
    if command -v yay &>/dev/null; then
        echo "✔ yay is already installed."
        return
    fi
    echo "==> Setting up yay AUR helper..."
    mkdir -p "$SOURCES_DIR"
    pushd "$SOURCES_DIR" >/dev/null
    git clone https://aur.archlinux.org/yay.git
    cd yay
    makepkg -si --noconfirm
    popd >/dev/null
}

install_aur() {
    echo "==> Installing AUR packages..."
    # Installing as a batch is much faster than a loop
    yay -S --needed --noconfirm "${aur_programs[@]}"
}

copy_configs() {
    echo "==> Applying Dotfiles..."
    [ -d "$REPOS_DIR" ] || { echo "Error: $REPOS_DIR not found"; return 1; }
    
    cd "$REPOS_DIR"
    
    # Fonts
    sudo mkdir -p /usr/local/share/fonts/
    [ -d "fonts" ] && sudo cp -rf fonts/* /usr/local/share/fonts/
    sudo fc-cache -fv

    # Configs (using -a for archive/recursive/preserve)
    mkdir -p ~/.config
    cp -ra .config/* ~/.config/
    
    # Home files
    for file in .bashrc .xinitrc .Xmodmap .fehbg; do
        [ -f "$file" ] && cp "$file" "$HOME/"
    done

    # Xmodmap setup
    XINITRC_GLOBAL="/etc/X11/xinit/xinitrc"
    LINE='xmodmap ~/.Xmodmap'
    if [ -f "$XINITRC_GLOBAL" ] && ! grep -Fxq "$LINE" "$XINITRC_GLOBAL"; then
        echo "$LINE" | sudo tee -a "$XINITRC_GLOBAL" > /dev/null
    fi
}

copy_system_configs() {
    echo "==> Applying System Rules..."
    cd "$REPOS_DIR"
    
    # Use -f to force/overwrite
    [ -f "50-libinput.conf" ] && sudo cp 50-libinput.conf /etc/X11/xorg.conf.d/
    [ -f "10-serverflags.conf" ] && sudo cp 10-serverflags.conf /etc/X11/xorg.conf.d/
    [ -f "99-removable.rules" ] && sudo cp 99-removable.rules /etc/udev/rules.d/
    
    # Walls
    sudo mkdir -p /usr/share/pixmaps
    [ -f "walls/background.jpeg" ] && sudo cp walls/background.jpeg /usr/share/pixmaps/
}

enable_services() {
    echo "==> Enabling Services..."
    sudo systemctl enable --now bluetooth
    
    # User services (only enable, don't start, as we aren't in a graphical session)
    # Note: These services must exist in ~/.config/systemd/user/
    user_svcs=(trayer volctl polkit picom nm-applet blueman-applet)
    for svc in "${user_svcs[@]}"; do
        systemctl --user enable "$svc" || echo "⚠️ Could not enable $svc (Expected if no D-Bus)"
    done
}

final_touches() {
    echo "==> Finalizing..."
    git config --global user.name "Abhishek Mishra"
    git config --global user.email "gmkng1@gmail.com"
    
    # Starship
    curl -sS https://starship.rs/install.sh | sh -s -- -y
    
    # Shell
    sudo chsh -s "$(command -v fish)" "$USER"
    
    mkdir -p ~/Pictures/Screenshots ~/Pictures/walls
    [ -d "$REPOS_DIR/walls" ] && cp -r "$REPOS_DIR/walls/"* ~/Pictures/walls/
}

main() {
    prep_system
    install_official
    setup_yay
    install_aur
    copy_configs
    copy_system_configs
    enable_services
    final_touches

    echo "🎉 Installation complete!"
    read -rp "🔁 Reboot now? (y/n): " answer
    [[ "$answer" =~ ^[Yy]$ ]] && sudo reboot
}

main
