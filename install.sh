#!/bin/bash
# WiFi Cracker Installation Script for UserLAnd/AnLinux/Linux

echo "=== WiFi Cracker Setup for UserLAnd/AnLinux/Linux ==="

# Detect environment
if [ -d "/data/data/tech.ula" ]; then
    echo "Detected: UserLAnd environment"
    ENV="userland"
elif [ -d "/data/data/exa.lnx.a" ]; then
    echo "Detected: AnLinux environment" 
    ENV="anlinux"
else
    echo "Detected: Standard Linux environment"
    ENV="linux"
fi

# Update system
echo "Updating system packages..."
if command -v apt >/dev/null 2>&1; then
    apt update && apt upgrade -y
elif command -v pkg >/dev/null 2>&1; then
    pkg update && pkg upgrade -y
fi

# Install required packages
echo "Installing required packages..."
if command -v apt >/dev/null 2>&1; then
    apt install -y python3 python3-pip wireless-tools net-tools iw curl wget sudo
elif command -v pkg >/dev/null 2>&1; then
    pkg install -y python3 python3-pip wireless-tools net-tools iw curl wget
fi

# Download and install Python dependencies
echo "Downloading and installing Python dependencies..."
curl -o ~/requirements.txt https://raw.githubusercontent.com/n0obcoders/wifiwps/main/requirements.txt
pip3 install --user -r ~/requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p ~/wifi_crack_results
mkdir -p ~/wordlists

# Download the WiFi Cracker script
echo "Setting up WiFi Cracker..."
curl -o ~/wifi_cracker_userland.py https://raw.githubusercontent.com/n0obcoders/wifiwps/main/wifi_cracker_userland.py
chmod +x ~/wifi_cracker_userland.py

echo "=== ✅ Installation Complete ==="
echo "👉 Run with: python3 ~/wifi_cracker_userland.py"
