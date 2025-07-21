#!/bin/bash
# WiFi Cracker Installation Script for UserLAnd/AnLinux

echo "=== WiFi Cracker Setup for UserLAnd/AnLinux ==="

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

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user colorama tabulate requests netifaces psutil

# Create directories
echo "Creating directories..."
mkdir -p ~/wifi_crack_results
mkdir -p ~/wordlists

# Download the script
echo "Setting up WiFi Cracker..."
curl -o ~/wifi_cracker_userland.py https://raw.githubusercontent.com/yourusername/wifi-cracker/main/wifi_cracker_userland.py
chmod +x ~/wifi_cracker_userland.py

echo "=== Installation Complete ==="
echo "Run with: python3 ~/wifi_cracker_userland.py"
