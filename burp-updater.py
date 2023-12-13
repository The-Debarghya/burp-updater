#!/usr/bin/env python3
import os
import argparse
import hashlib
import requests
import subprocess
import tarfile

from rich.console import Console
from rich.progress import Progress
import time


BASE_URL = "https://portswigger.net/burp/releases/data?pageSize=10"
DEFAULT_INSTALLATION_DIR = "/opt"

def get_current_version() -> str:
    version = subprocess.run(['BurpSuiteCommunity', '--version'], capture_output=True).stdout.decode('utf-8').split(' ')[2]
    return version

def verify_version(version: str) -> bool:
    pass

def get_available_versions() -> list:
    pass

def download_new_installer(version: str, platform: str, product_id: str) -> str:
    pass      
    
def uninstall_old_version() -> str:
    pass
    
def install_from_installer(installer_path: str):
    pass

def cleanup(downloaded_installer: str):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update Burp Suite')
    parser.add_argument('-v', '--version', help='Update to version')
    parser.add_argument('-i', '--product-id', help='Update for product type [Default community]', default='community', choices=['community', 'pro', 'enterprise'])
    parser.add_argument('-p', '--platform', help='Update for platform [Default Linux]', default='Linux', choices=['Linux', 'LinuxArm64', 'Jar', 'MacOsArm64', 'MaxOsx', 'WindowsX64', 'AgentUpdate', 'Kubernetes', 'Updater'])
    parser.add_argument('--download-only', help='Download installer only', action='store_true')
    parser.add_argument('--install-only', help='Install from already downloaded installer only', action='store_true')
    parser.add_argument('--file', help='Path to downloaded archive')
    parser.add_argument('--uninstall-only', help='Uninstall old installation only', action='store_true')
    parser.add_argument('--available-versions', help='Show available versions', action='store_true')
    #parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
    version = get_current_version()
    parser.add_argument('-c', '--current', help='Get current version status', action='version', version=version)

    args = parser.parse_args()
    if not verify_version(args.version):
        print(f'Already on version {args.version}')
        exit(0)

    if args.available_versions:
        pass

    if args.download_only:
        pass

    if args.install_only:
        pass

    if args.uninstall_only:
        pass
        
    try:
        pass
    except Exception as e:
        print(f'Error: {e.__str__()}')
        exit(1)
    
