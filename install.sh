#!/bin/bash

# echo "Updating mirrors"
# cd mirror
# # Update mirror list
# ./get_mirror.sh
# cd

# # List of programs to install
# programs=(
#     "qtile"
#     "neovim"
#     "git"
#     "htop"
#     "curl"
#     "wget"
#     "firefox"
#     "lxsession"
#     "terminator"
#     "rofi"
#     "picom"
#     "font-manager"
#     "blueman"
#     "bluez"
#     "bluez-utils"
#     "nitrogen"
#     "pulseaudio"
#     "pavucontrol"
#     "brightnessctl"
#     "pamixer"
#     "alsa-plugins"
#     "alsa-utils"
#     "pulseaudio-bluetooth"
#     "xarchiver"
#     "zip"
#     "unzip"
#     "unrar"
#     "p7zip"
#     # "nemo"
#     "python-dbus-next"
#     "mtpfs"
#     "gvfs-mtp"
#     "gvfs-gphoto2"
#     "telegram-desktop"
#     "trayer"
#     "lxappearance"
#     "lightdm-slick-greeter"
#     "xfce4-screenshooter"
#     "upower"
#     "sxiv"
#     "mpv"
#     "grub-customizer"
#     "gnome-disk-utility"
#     "telegram-desktop"
#     "kdeconnect"
#     "volctl"
# 	"pcmanfm"
# 	# "zsh"
# 	"ripgrep"
#     "xfce4-power-manager"
#     "tlp" 
#     "tlp-rdw"
# )

# # Update the package database and upgrade the system
# echo "Updating the package database and upgrading the system..."
# sudo pacman -Syu --noconfirm

# # Install each program in the list
# echo "Installing programs..."
# for program in "${programs[@]}"; do
#     if pacman -Qi $program &> /dev/null; then
#         echo "$program is already installed."
#     else
#         sudo pacman -S --noconfirm $program
#     fi
# done

# # Create a Sources directory and clone yay
# echo "Setting up yay AUR helper..."
# mkdir -p ~/Sources
# cd ~/Sources
# if [ ! -d "yay" ]; then
#     git clone https://aur.archlinux.org/yay.git
# else
#     echo "yay directory already exists. Skipping clone."
# fi

# # Build and install yay
# cd yay
# makepkg -si --noconfirm

# # List of AUR programs to install via yay
# aur_programs=(
#     "visual-studio-code-bin"
#     "betterlockscreen"
#     "dracula-gtk-theme-full"
#     "dracula-icons-git"
#     "envycontrol"
#     "pfetch"
#     "python-pulsectl"
#     "jmtpfs"
#     "lightdm-settings"
#     "python-colorthief"
#     "volctl"
#     "qtile-extras"
#     "nomacs"
#     "brightnessctl"
# )

# # Install each AUR program via yay
# echo "Installing AUR programs via yay..."
# for aur_program in "${aur_programs[@]}"; do
#     yay -S --noconfirm $aur_program
# done

# # Change to the newqtile_test directory
# cd ~/newqtile_test

# # Additional commands for fonts setup
# echo "Setting up fonts..."
# sudo cp -rT fonts /usr/local/share/fonts/
# sudo fc-cache -vf

# # Copy .config directory to the home directory
# echo "Copying .config directory to the home directory..."
# cp -rT .config ~/.config/

# # Copy .bashrc to the home directory
# echo "Copying .bashrc to the home directory..."
# cp -T .bashrc ~/.bashrc

# # Copy .Xmodmap to the home directory
# echo "Copying .Xmodmap to the home directory..."
# cp -T .bashrc ~/.Xmodmap

# # Copy .zshrc to the home directory
# echo "Copying zshrc to the home directory..."
# cp -T .zshrc ~/.zshrc

# # Adding Xmodmap file to xinitrc so it can run automaticly
# echo "Adding Xmodmap file to xinitr"
# TEXT_FILE="/etc/X11/xinit/xinitrc"
# LINE_TO_ADD="xmodmap ~/.Xmodmap"
# sudo echo "$LINE_TO_ADD" >> "$TEXT_FILE"
# echo "Line added to $TEXT_FILE"

# # Copy 50-libinput.conf to /etc/X11/xorg.conf.d/
# echo "Copying 50-libinput.conf and 10-serverflags.conf to /etc/X11/xorg.conf.d/..."
# sudo cp 50-libinput.conf /etc/X11/xorg.conf.d/
# sudo cp 10-serverflags.conf /etc/X11/xorg.conf.d/
# echo "Copying thunderbolt configration"
# sudo cp 99-removable.rules /etc/udev/rules.d/

# # Enable Bluetooth service
# echo "Enabling Bluetooth service..."
# sudo systemctl enable bluetooth
# sudo systemctl start bluetooth

# # Copy lightdm config
# echo "Copying lightdm configration to /etc/"
# sudo cp -rT lightdm /etc/lightdm

# # Copy Grub theme config
# echo "Copying Grub themes configration to /boot/"
# sudo cp -rT grub /boot/grub/

# # Configration for Abhishek Mishra only
# git config --global user.name "Abhishek Mishra"
# git config --global user.email gmkng1@gmail.com

# mkdir -p  ~/Pictures/Screenshots
# cp -rT walls   ~/Pictures/walls


# echo "Installation complete!"




set -e  # Exit on error
set -o pipefail

echo "==> Updating mirror list..."
cd mirror && ./get_mirror.sh && cd ~

# List of packages from official repos
programs=(
    qtile neovim git htop curl wget firefox lxsession terminator rofi picom
    font-manager blueman bluez bluez-utils pulseaudio pavucontrol
    brightnessctl pamixer alsa-plugins alsa-utils pulseaudio-bluetooth
    xarchiver zip unzip unrar p7zip python-dbus-next mtpfs gvfs-mtp gvfs-gphoto2
    telegram-desktop trayer lxappearance lightdm-slick-greeter xfce4-screenshooter
    upower sxiv mpv grub-customizer gnome-disk-utility kdeconnect volctl pcmanfm
    ripgrep xfce4-power-manager tlp tlp-rdw
)

# List of AUR packages
aur_programs=(
    visual-studio-code-bin betterlockscreen dracula-gtk-theme-full dracula-icons-git
    envycontrol pfetch python-pulsectl jmtpfs lightdm-settings python-colorthief
    volctl qtile-extras nomacs brightnessctl nitrogen
)

install_programs() {
    echo "==> Updating system..."
    sudo pacman -Syu --noconfirm

    echo "==> Installing official packages..."
    for program in "${programs[@]}"; do
        if pacman -Qi "$program" &>/dev/null; then
            echo "✔ $program is already installed."
        else
            sudo pacman -S --noconfirm "$program"
        fi
    done
}

setup_yay() {
    echo "==> Setting up yay AUR helper..."
    mkdir -p ~/Sources
    cd ~/Sources

    if [ ! -d "yay" ]; then
        git clone https://aur.archlinux.org/yay.git
    else
        echo "✔ yay already cloned."
    fi

    cd yay
    makepkg -si --noconfirm
}

install_aur_programs() {
    echo "==> Installing AUR packages..."
    for aur_program in "${aur_programs[@]}"; do
        yay -S --noconfirm "$aur_program"
    done
}

copy_configs() {
    echo "==> Setting up configuration files..."
    cd ~/newqtile_test

    echo "📁 Copying fonts..."
    sudo cp -rT fonts /usr/local/share/fonts/
    sudo fc-cache -vf

    echo "📁 Copying .config directory..."
    cp -rT .config ~/.config/

    echo "📄 Copying dotfiles..."
    cp -T .bashrc ~/.bashrc
    cp -T .Xmodmap ~/.Xmodmap
    cp -T .zshrc ~/.zshrc

    echo "🧠 Adding Xmodmap to xinitrc..."
    XINITRC="/etc/X11/xinit/xinitrc"
    LINE='xmodmap ~/.Xmodmap'
    if ! grep -Fxq "$LINE" "$XINITRC"; then
        echo "$LINE" | sudo tee -a "$XINITRC" > /dev/null
        echo "✔ Added to $XINITRC"
    else
        echo "✔ Xmodmap line already exists in $XINITRC"
    fi
}

copy_system_configs() {
    echo "==> Copying system configuration files..."

    sudo cp 50-libinput.conf /etc/X11/xorg.conf.d/
    sudo cp 10-serverflags.conf /etc/X11/xorg.conf.d/
    sudo cp 99-removable.rules /etc/udev/rules.d/
    sudo cp -rT lightdm /etc/lightdm
    sudo cp -rT grub /boot/grub/
}

enable_services() {
    echo "==> Enabling services..."
    sudo systemctl enable bluetooth
    sudo systemctl start bluetooth
}

final_touches() {
    echo "==> Final touches..."

    git config --global user.name "Abhishek Mishra"
    git config --global user.email "gmkng1@gmail.com"

    mkdir -p ~/Pictures/Screenshots
    cp -rT walls ~/Pictures/walls
}

main() {
    install_programs
    setup_yay
    install_aur_programs
    copy_configs
    copy_system_configs
    enable_services
    final_touches
    echo "🎉 Installation complete!"

    # Prompt for reboot
    read -rp "🔁 Do you want to reboot now? (y/n): " answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo "Rebooting system..."
        sudo reboot
    else
        echo "Reboot skipped. Please reboot manually later to apply all changes."
    fi
}
main

