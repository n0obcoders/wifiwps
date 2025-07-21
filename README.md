# WiFi WPS Cracker 🔐

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-UserLAnd%20%7C%20Linux%20%7C%20AnLinux-yellow.svg)]()

> ⚠️ For **educational purposes only**. Use only on networks you own or have permission to test.

# 🔐 WiFi Pentesting Toolkit – UserLAnd / AnLinux Compatible

A simulated, ethical WiFi pentesting toolkit built in Python — designed to run on **UserLAnd**, **AnLinux**, **Termux**, and **standard Linux** distributions.

⚠️ **For educational and authorized testing purposes only. Do not use this tool on networks without explicit permission.**

---

## 📌 Features

- 🔍 Multi-method WiFi network scanning (`iwlist`, `iw`, `nmcli`, `/proc/net/wireless`)
- 📂 Auto wordlist generation from target ESSID
- ☁️ Download popular SecLists wordlists
- 🔓 Simulated WPA/WPA2 bruteforce attacks
- 🔑 Simulated WPS PIN attacks (common, sequential, pattern-based)
- 📜 Logging & reporting
- 💡 System diagnostics & dependency check
- ✅ Compatible with:
  - UserLAnd / AnLinux
  - Kali Linux (VM)
  - Termux (rooted preferred)
  - Standard Linux (Debian/Ubuntu)
  - Pydroid (limited)

---

## 🚀 Getting Started

## 📦 Installation (UserLAnd / AnLinux / Ubuntu / Kali)

Run the following commands in your terminal:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip wireless-tools net-tools iw curl wget

# Install Python dependencies
pip3 install colorama tabulate requests netifaces psutil

# Clone the project
git clone https://github.com/n0obcoders/wifiwps.git
cd wifiwps

# Run the tool
python3 wifi_pentest.py

