#!/usr/bin/env python3
# WiFi Penetration Testing Tool - Compatible with UserLAnd/AnLinux
# Version: 2.0 - UserLAnd Compatible
# WARNING: For educational and authorized testing only!

import os
import sys
import time
import subprocess
import re
import threading
import json
import random
import socket
from datetime import datetime
from pathlib import Path

# Dependency check and imports
def check_dependencies():
    required_packages = ["colorama", "tabulate", "requests", "netifaces", "psutil"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)

check_dependencies()

from colorama import init, Fore, Style
from tabulate import tabulate
import requests
import netifaces
import psutil

init(autoreset=True)

class UserLandWiFiCracker:
    def __init__(self):
        self.interface = self.get_wireless_interface()
        self.results_dir = Path("wifi_crack_results")
        self.wordlists_dir = Path("wordlists")
        self.session_log = self.results_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        self.results_dir.mkdir(exist_ok=True)
        self.wordlists_dir.mkdir(exist_ok=True)

        self.targets = []
        self.current_target = None
        self.is_userland = self.check_userland_environment()
        self.is_anlinux = self.check_anlinux_environment()
        self.attack_running = False

        self.log(f"WiFi Cracker Started - {datetime.now()}")
        self.log(f"Interface: {self.interface}")
        self.log(f"Environment: {'UserLAnd' if self.is_userland else 'AnLinux' if self.is_anlinux else 'Standard Linux'}")

    def check_userland_environment(self):
        return os.path.exists("/data/data/tech.ula") or "userland" in os.environ.get("USER", "").lower()

    def check_anlinux_environment(self):
        return os.path.exists("/data/data/exa.lnx.a") or "anlinux" in str(os.getcwd()).lower()

    def get_wireless_interface(self):
        try:
            interfaces = netifaces.interfaces()
            for iface in interfaces:
                if any(x in iface.lower() for x in ["wlan", "wl", "wifi", "wireless"]):
                    return iface
            if os.path.exists("/proc/net/wireless"):
                with open("/proc/net/wireless", "r") as f:
                    lines = f.readlines()
                    for line in lines[2:]:
                        if line.strip():
                            iface = line.split(":")[0].strip()
                            return iface
            try:
                result = subprocess.run(["ip", "link", "show"], capture_output=True, text=True)
                for line in result.stdout.split("\n"):
                    if "wlan" in line or "wl" in line:
                        match = re.search(r"\d+:\s+(\w+):", line)
                        if match:
                            return match.group(1)
            except:
                pass
            return "wlan0"
        except Exception as e:
            self.log(f"Interface detection error: {e}", "WARNING")
            return "wlan0"

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        color_map = {
            "ERROR": Fore.RED,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "INFO": Fore.CYAN,
            "DEBUG": Fore.MAGENTA
        }
        color = color_map.get(level, Fore.CYAN)
        print(f"{color}[{level}] {message}{Style.RESET_ALL}")
        try:
            with open(self.session_log, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Logging error: {e}")

    def banner(self):
        banner = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════════════╗
║                    WiFi Penetration Testing Tool                    ║
║                        UserLAnd/AnLinux Compatible                  ║
║                         Version 2.0                                 ║
╚══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

Environment: {'UserLAnd' if self.is_userland else 'AnLinux' if self.is_anlinux else 'Standard Linux'}
Interface: {self.interface}
{Fore.YELLOW}⚠️  WARNING: For educational and authorized testing only!{Style.RESET_ALL}
"""
        print(banner)

    def scan_networks(self):
        self.log("Starting network scan...", "INFO")
        self.targets = []
        methods = [
            self.android_wifi_scan,
            self.iwlist_scan,
            self.iw_scan,
            self.nmcli_scan,
            self.proc_scan
        ]
        for method in methods:
            try:
                if method():
                    if self.targets:
                        self.log(f"Scan successful using {method.__name__}", "SUCCESS")
                        return True
            except Exception as e:
                self.log(f"{method.__name__} failed: {e}", "DEBUG")
        if not self.targets:
            self.log("Real scanning failed, generating demo targets...", "WARNING")
            self.generate_demo_targets()
            return True
        return False

    def android_wifi_scan(self):
        try:
            wifi_files = [
                "/proc/net/wireless",
                "/sys/class/net/wlan0/wireless/",
                "/data/misc/wifi/wpa_supplicant.conf"
            ]
            for wifi_file in wifi_files:
                if os.path.exists(wifi_file):
                    self.log(f"Found WiFi interface info at {wifi_file}", "DEBUG")
            result = subprocess.run(["ip", "addr", "show", self.interface],
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and "UP" in result.stdout:
                self.log("WiFi interface is UP", "INFO")
                return False
        except Exception as e:
            self.log(f"Android WiFi scan error: {e}", "DEBUG")
        return False

    def iwlist_scan(self):
        try:
            self.log("Scanning with iwlist...", "INFO")
            subprocess.run(["sudo", "ip", "link", "set", self.interface, "up"],
                           capture_output=True, timeout=5)
            result = subprocess.run(["sudo", "iwlist", self.interface, "scan"],
                                   capture_output=True, text=True, timeout=45)
            if result.returncode != 0:
                return False
            targets = []
            current_cell = {}
            for line in result.stdout.split("\n"):
                line = line.strip()
                if "Cell" in line and "Address" in line:
                    if current_cell and current_cell.get("bssid"):
                        targets.append(current_cell)
                    current_cell = {}
                    bssid_match = re.search(r"Address: ([A-Fa-f0-9:]+)", line)
                    current_cell["bssid"] = bssid_match.group(1) if bssid_match else "Unknown"
                elif "ESSID" in line:
                    essid_match = re.search(r'ESSID:"(.*)"', line)
                    current_cell["essid"] = essid_match.group(1) if essid_match else "Hidden"
                elif "Signal level" in line:
                    signal_match = re.search(r"Signal level=([-0-9]+)", line)
                    current_cell["level"] = signal_match.group(1) + " dBm" if signal_match else "Unknown"
                elif "WPA2" in line:
                    current_cell["encryption"] = "WPA/WPA2"
                elif "WPA Version" in line:
                    current_cell["encryption"] = "WPA"
                elif "Encryption key:on" in line:
                    if "encryption" not in current_cell:
                        current_cell["encryption"] = "WEP"
            if current_cell and current_cell.get("bssid"):
                targets.append(current_cell)
            self.targets = targets
            self.log(f"Found {len(targets)} networks", "SUCCESS")
            return len(targets) > 0
        except Exception as e:
            self.log(f"iwlist error: {e}", "ERROR")
            return False

    def iw_scan(self):
        try:
            self.log("Scanning with iw...", "INFO")
            result = subprocess.run(["sudo", "iw", "dev", self.interface, "scan"],
                                   capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False
            targets = []
            current_bss = {}
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line.startswith("BSS "):
                    if current_bss and current_bss.get("bssid"):
                        targets.append(current_bss)
                    current_bss = {}
                    bssid_match = re.search(r"BSS ([a-f0-9:]+)", line)
                    current_bss["bssid"] = bssid_match.group(1) if bssid_match else "Unknown"
                elif "SSID:" in line:
                    ssid = line.split("SSID: ")[1] if "SSID: " in line else "Hidden"
                    current_bss["essid"] = ssid
                elif "signal:" in line:
                    signal_match = re.search(r"signal: ([-0-9.]+)", line)
                    current_bss["level"] = signal_match.group(1) + " dBm" if signal_match else "Unknown"
                elif "WPA" in line or "RSN" in line:
                    current_bss["encryption"] = "WPA/WPA2"
            if current_bss and current_bss.get("bssid"):
                targets.append(current_bss)
            self.targets = targets
            self.log(f"Found {len(targets)} networks", "SUCCESS")
            return len(targets) > 0
        except Exception as e:
            self.log(f"iw scan error: {e}", "ERROR")
            return False

    def nmcli_scan(self):
        try:
            self.log("Scanning with nmcli...", "INFO")
            subprocess.run(["nmcli", "dev", "wifi", "rescan"],
                           capture_output=True, timeout=10)
            time.sleep(2)
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,BSSID,MODE,CHAN,FREQ,RATE,SIGNAL,BARS,SECURITY", "dev", "wifi"],
                capture_output=True, text=True, timeout=20)
            if result.returncode != 0:
                return False
            targets = []
            for line in result.stdout.split("\n"):
                if line.strip():
                    parts = line.split(":")
                    if len(parts) >= 9:
                        target = {
                            "essid": parts[0] if parts[0] else "Hidden",
                            "bssid": parts[1],
                            "level": parts[6] + " dBm" if parts[6] else "Unknown",
                            "encryption": "WPA/WPA2" if parts[8] else "Open"
                        }
                        targets.append(target)
            self.targets = targets
            self.log(f"Found {len(targets)} networks", "SUCCESS")
            return len(targets) > 0
        except Exception as e:
            self.log(f"nmcli scan error: {e}", "ERROR")
            return False

    def proc_scan(self):
        try:
            if os.path.exists("/proc/net/wireless"):
                with open("/proc/net/wireless", "r") as f:
                    lines = f.readlines()
                    if len(lines) > 2:
                        self.log("Found wireless interface in /proc/net/wireless", "INFO")
                        return False
        except Exception as e:
            self.log(f"Proc scan error: {e}", "DEBUG")
        return False

    def generate_demo_targets(self):
        demo_networks = [
            {"essid": "WiFi-Home-Network", "bssid": "AA:BB:CC:DD:EE:01", "encryption": "WPA/WPA2", "level": "-45 dBm"},
            {"essid": "Office-WiFi", "bssid": "AA:BB:CC:DD:EE:02", "encryption": "WPA/WPA2", "level": "-52 dBm"},
            {"essid": "Public-WiFi", "bssid": "AA:BB:CC:DD:EE:03", "encryption": "Open", "level": "-68 dBm"},
            {"essid": "Neighbor-WiFi", "bssid": "AA:BB:CC:DD:EE:04", "encryption": "WEP", "level": "-71 dBm"},
            {"essid": "Hidden", "bssid": "AA:BB:CC:DD:EE:05", "encryption": "WPA/WPA2", "level": "-78 dBm"},
        ]
        self.targets = demo_networks
        self.log(f"Generated {len(demo_networks)} demo networks", "WARNING")

    def display_targets(self):
        if not self.targets:
            self.log("No targets to display.", "WARNING")
            return
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"DISCOVERED NETWORKS ({len(self.targets)} found)")
        print(f"{'='*80}{Style.RESET_ALL}")
        headers = ["#", "ESSID", "BSSID", "Encryption", "Signal"]
        table_data = []
        for i, target in enumerate(self.targets, 1):
            essid = target.get("essid", "Unknown")[:25]
            bssid = target.get("bssid", "Unknown")[:17]
            encryption = target.get("encryption", "Unknown")
            level = str(target.get("level", "Unknown"))[:10]
            table_data.append([i, essid, bssid, encryption, level])
        print(tabulate(table_data, headers, tablefmt="fancy_grid"))

    def generate_wordlist(self, target_essid=None):
        self.log("Generating wordlist...", "INFO")
        passwords = set()
        common_base = [
            "password", "123456", "password123", "admin", "12345678", "qwerty",
            "abc123", "Password1", "welcome", "letmein", "monkey", "1234567890",
            "dragon", "trustno1", "hello", "sunshine", "master", "123123",
            "football", "jesus", "ninja", "mustang", "access", "shadow",
            "michael", "superman", "696969", "123qwe", "freedom", "batman"
        ]
        passwords.update(common_base)
        if target_essid and target_essid != "Hidden":
            essid_variations = [
                target_essid, target_essid.lower(), target_essid.upper(),
                target_essid.capitalize(), target_essid.replace(" ", ""),
                target_essid.replace("-", ""), target_essid.replace("_", "")
            ]
            for var in essid_variations:
                passwords.update([
                    var, f"{var}123", f"{var}321", f"{var}1234", f"123{var}",
                    f"{var}!", f"{var}password", f"password{var}", f"{var}admin",
                    f"admin{var}", f"{var}2023", f"{var}2024"
                ])
        for i in range(10000000, 100000000, 11111111):
            passwords.add(str(i))
        final_passwords = [pwd for pwd in passwords if 8 <= len(pwd) <= 63]
        wordlist_file = self.wordlists_dir / "generated_wordlist.txt"
        with open(wordlist_file, "w") as f:
            for pwd in sorted(final_passwords):
                f.write(pwd + "\n")
        self.log(f"Generated {len(final_passwords)} passwords in {wordlist_file}", "SUCCESS")
        return wordlist_file

    def download_wordlists(self):
        wordlists = {
            "common-passwords.txt": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt",
            "wifi-passwords.txt": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/WiFi-WPA/probable-v2-wpa-top4800.txt"
        }
        for filename, url in wordlists.items():
            filepath = self.wordlists_dir / filename
            if filepath.exists():
                self.log(f"{filename} already exists", "INFO")
                continue
            try:
                self.log(f"Downloading {filename}...", "INFO")
                response = requests.get(url, timeout=60, stream=True)
                response.raise_for_status()
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.log(f"Downloaded {filename}", "SUCCESS")
            except Exception as e:
                self.log(f"Failed to download {filename}: {e}", "ERROR")

    def continuous_bruteforce_attack(self, wordlist_paths):
        if not self.current_target:
            self.log("No target selected.", "ERROR")
            return None
        target_name = self.current_target.get("essid", "Unknown")
        self.log(f"Starting SIMULATED bruteforce on {target_name}", "INFO")
        self.log("⚠️  This is a SIMULATION - no real attacks are performed", "WARNING")
        self.attack_running = True
        attempt_count = 0
        start_time = time.time()
        try:
            while self.attack_running:
                for wordlist_path in wordlist_paths:
                    if not self.attack_running:
                        break
                    if not os.path.exists(wordlist_path):
                        self.log(f"Wordlist not found: {wordlist_path}", "WARNING")
                        continue
                    self.log(f"Processing wordlist: {wordlist_path}", "INFO")
                    try:
                        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
                            for line in f:
                                if not self.attack_running:
                                    break
                                password = line.strip()
                                if not password or len(password) < 8:
                                    continue
                                attempt_count += 1
                                time.sleep(random.uniform(0.001, 0.01))
                                if attempt_count % 100 == 0:
                                    elapsed = time.time() - start_time
                                    rate = attempt_count / elapsed if elapsed > 0 else 0
                                    self.log(f"Tried {attempt_count} passwords ({rate:.1f}/sec) - Current: {password[:20]}...", "INFO")
                                if self.simulate_attack_success(password):
                                    elapsed = time.time() - start_time
                                    self.log(f"SIMULATED SUCCESS - PASSWORD: {password}", "SUCCESS")
                                    self.log(f"Time: {elapsed:.2f}s, Attempts: {attempt_count}", "SUCCESS")
                                    self.save_result(target_name, password, "Bruteforce", attempt_count, elapsed)
                                    return password
                    except Exception as e:
                        self.log(f"Error reading {wordlist_path}: {e}", "ERROR")
                self.log("Completed all wordlists, restarting cycle...", "INFO")
        except KeyboardInterrupt:
            self.log("Attack stopped by user", "WARNING")
        elapsed = time.time() - start_time
        self.log(f"Attack ended after {attempt_count} attempts ({elapsed:.2f}s)", "INFO")
        return None

    def continuous_wps_attack(self):
        if not self.current_target:
            self.log("No target selected.", "ERROR")
            return None
        target_name = self.current_target.get("essid", "Unknown")
        self.log(f"Starting SIMULATED WPS PIN attack on {target_name}", "INFO")
        self.log("⚠️  This is a SIMULATION - no real attacks are performed", "WARNING")
        pin_lists = {
            "Common PINs": [
                "12345670", "00000000", "11111111", "22222222", "33333333",
                "44444444", "55555555", "66666666", "77777777", "88888888",
                "99999999", "12345678", "87654321", "11223344", "55667788"
            ],
            "Sequential PINs": [str(i).zfill(8) for i in range(0, 100000000, 1111)],
            "Pattern PINs": []
        }
        for i in range(1000, 10000):
            pin_lists["Pattern PINs"].extend([
                f"{i}{i}",
                f"{str(i)[::-1]}{i}",
                f"{i}1234"
            ])
        self.attack_running = True
        total_attempts = 0
        start_time = time.time()
        try:
            while self.attack_running:
                for strategy, pins in pin_lists.items():
                    if not self.attack_running:
                        break
                    self.log(f"Trying {strategy} ({len(pins)} PINs)", "INFO")
                    for pin in pins:
                        if not self.attack_running:
                            break
                        total_attempts += 1
                        time.sleep(random.uniform(0.5, 2.0))
                        if self.simulate_wps_success(pin):
                            elapsed = time.time() - start_time
                            self.log(f"SIMULATED WPS SUCCESS - PIN: {pin}", "SUCCESS")
                            self.log(f"Time: {elapsed:.2f}s, Attempts: {total_attempts}", "SUCCESS")
                            self.save_result(target_name, pin, "WPS", total_attempts, elapsed)
                            return pin
                        if total_attempts % 10 == 0:
                            elapsed = time.time() - start_time
                            rate = total_attempts / elapsed if elapsed > 0 else 0
                            self.log(f"Tried {total_attempts} PINs ({rate:.2f}/sec) - Current: {pin}", "INFO")
                self.log("Completed all PIN lists, restarting cycle...", "INFO")
        except KeyboardInterrupt:
            self.log("WPS attack stopped by user", "WARNING")
        elapsed = time.time() - start_time
        self.log(f"WPS attack ended after {total_attempts} attempts ({elapsed:.2f}s)", "INFO")
        return None

    def simulate_attack_success(self, password):
        return random.random() < 0.001

    def simulate_wps_success(self, pin):
        if pin in ["12345670", "00000000"]:
            return random.random() < 0.02
        return random.random() < 0.005

    def save_result(self, target_name, credential, attack_type, attempts, time_taken):
        result_file = self.results_dir / f"{attack_type.lower()}_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(result_file, "w") as f:
            f.write(f"Target: {target_name}\n")
            f.write(f"BSSID: {self.current_target.get('bssid', 'Unknown')}\n")
            f.write(f"Attack Type: {attack_type}\n")
            f.write(f"Credential Found: {credential}\n")
            f.write(f"Attempts: {attempts}\n")
            f.write(f"Time Taken: {time_taken:.2f} seconds\n")
            f.write(f"Timestamp: {datetime.now()}\n")
        self.log(f"Results saved to {result_file}", "SUCCESS")

    def show_system_info(self):
        print(f"\n{Fore.CYAN}{'='*60}")
        print("SYSTEM INFORMATION")
        print("="*60)
        env_info = []
        if self.is_userland:
            env_info.append("UserLAnd")
        if self.is_anlinux:
            env_info.append("AnLinux")
        print(f"Environment: {', '.join(env_info) if env_info else 'Standard Linux'}")
        try:
            interfaces = netifaces.interfaces()
            print(f"Network Interfaces: {', '.join(interfaces)}")
            print(f"Selected Interface: {self.interface}")
        except:
            print("Network Interfaces: Unable to detect")
        try:
            print(f"Python Version: {sys.version.split()[0]}")
            print(f"Working Directory: {os.getcwd()}")
            print(f"User: {os.environ.get('USER', 'Unknown')}")
        except:
            pass
        tools = ["iwlist", "iw", "nmcli", "ip", "sudo"]
        print(f"\nTool Availability:")
        for tool in tools:
            try:
                result = subprocess.run(["which", tool], capture_output=True, text=True)
                available = "✓" if result.returncode == 0 else "✗"
                path = result.stdout.strip() if result.returncode == 0 else "Not found"
                print(f"  {tool}: {available} {path}")
            except:
                print(f"  {tool}: ✗ Check failed")
        print(f"\nPermissions:")
        try:
            result = subprocess.run(["sudo", "-n", "true"], capture_output=True, text=True)
            sudo_available = "✓" if result.returncode == 0 else "✗ (may require password)"
            print(f"  Sudo access: {sudo_available}")
        except:
            print(f"  Sudo access: ✗ Not available")
        try:
            if os.path.exists(f"/sys/class/net/{self.interface}"):
                with open(f"/sys/class/net/{self.interface}/operstate", "r") as f:
                    state = f.read().strip()
                print(f"  Interface {self.interface} state: {state}")
            else:
                print(f"  Interface {self.interface}: Not found in /sys/class/net/")
        except:
            print(f"  Interface status: Unable to check")
        print(f"="*60)

def main():
    cracker = UserLandWiFiCracker()
    cracker.banner()
    while True:
        print(f"\n{Fore.CYAN}{'='*60}")
        print("WiFi Cracker - Main Menu")
        print("="*60)
        print("1. Scan Networks")
        print("2. Select Target")
        print("3. Generate Wordlist")
        print("4. Download Wordlists")
        print("5. Simulated Bruteforce Attack")
        print("6. Simulated WPS PIN Attack")
        print("7. Stop Current Attack")
        print("8. System Information")
        print("0. Exit")
        print("="*60)
        choice = input(f"{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}").strip()
        if choice == "1":
            cracker.scan_networks()
            if cracker.targets:
                cracker.display_targets()
        elif choice == "2":
            if not cracker.targets:
                cracker.log("Run a scan first!", "WARNING")
                continue
            cracker.display_targets()
            try:
                selection = int(input("Enter target number: "))
                if 1 <= selection <= len(cracker.targets):
                    cracker.current_target = cracker.targets[selection - 1]
                    target_info = f"{cracker.current_target.get('essid')} ({cracker.current_target.get('bssid')})"
                    cracker.log(f"Selected: {target_info}", "SUCCESS")
                else:
                    cracker.log("Invalid selection", "ERROR")
            except ValueError:
                cracker.log("Invalid input", "ERROR")
        elif choice == "3":
            target_essid = cracker.current_target.get("essid") if cracker.current_target else None
            cracker.generate_wordlist(target_essid)
        elif choice == "4":
            cracker.download_wordlists()
        elif choice == "5":
            if not cracker.current_target:
                cracker.log("Select a target first!", "WARNING")
                continue
            wordlist_files = []
            for file in cracker.wordlists_dir.glob("*.txt"):
                wordlist_files.append(str(file))
            if not wordlist_files:
                cracker.log("No wordlists found! Generate or download some first.", "WARNING")
                continue
            cracker.log(f"Using {len(wordlist_files)} wordlists", "INFO")
            cracker.continuous_bruteforce_attack(wordlist_files)
        elif choice == "6":
            if not cracker.current_target:
                cracker.log("Select a target first!", "WARNING")
                continue
            cracker.continuous_wps_attack()
        elif choice == "7":
            cracker.attack_running = False
            cracker.log("Stopping current attack...", "INFO")
        elif choice == "8":
            cracker.show_system_info()
        elif choice == "0":
            cracker.attack_running = False
            print(f"\n{Fore.RED}Exiting WiFi Cracker. Goodbye!{Style.RESET_ALL}")
            break
        else:
            cracker.log("Invalid choice", "ERROR")

if __name__ == "__main__":
    main()
