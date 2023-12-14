#!/usr/bin/env python3
import os
import argparse
import hashlib
import requests
import subprocess

from rich.console import Console
from rich.progress import Progress
import time

API_URL = "https://portswigger.net/burp/releases/data?pageSize=500"
DOWNLOAD_URL = "https://portswigger-cdn.net/burp/releases/download?product=community"
DEFAULT_INSTALLATION_DIR = "/opt/BurpSuiteCommunity"

def get_current_version() -> str:
    version = subprocess.run(['BurpSuiteCommunity', '--version'], capture_output=True).stdout.decode('utf-8').split(' ')[0]
    return version.split('-')[0]

def verify_version(version: str, current_version: str) -> bool:
    burp_exists = subprocess.run(['which', 'BurpSuiteCommunity'], capture_output=True).returncode == 0
    if burp_exists:
        return version != current_version
    return True

def get_available_versions() -> list:
    console = Console()
    with console.status("[bold green]Fetching available versions...") as status:
        try:
            status.start()
            result_set = requests.get(API_URL).json()['ResultSet']
            results = result_set['Results']
            versions = []
            for result in results:
                if result['productType'] != 'pro' or result['productType'] != 'enterprise':
                    versions.append((result['version'], result['releaseChannels']))
            time.sleep(0.1)
            status.update()
            return versions
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return None
        finally:
            status.stop()

def download_new_installer(version: str, platform: str) -> str:
    console = Console()
    with console.status("[bold green]Checking for specified version...") as status:
        status.start()
        result_set = requests.get(API_URL).json()['ResultSet']
        results = result_set['Results']
        for result in results:
            if result['version'] == version:
                builds = result['builds']
                break
        for build in builds:
            if build['ProductId'] == 'community' and build['ProductPlatform'] == platform and build['Version'] == version:
                filename = 'burpsuite_community_' + platform.lower() + '_v' + version.replace('.', '_') + '.sh'
                filehash = build['Sha256Checksum']
                break
        status.update()
        time.sleep(0.1)
        status.stop()    
    
    with requests.get(DOWNLOAD_URL + f'&version={version}&type={platform}', stream=True) as r:
        r.raise_for_status()
        progress = Progress()
        with Progress() as progress:
            file_size = int(r.headers['Content-Length'])
            task = progress.add_task(f"[cyan]Downloading {filename}...", total=file_size, start=True)
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))
            progress.stop()

    with console.status("[bold green]Verifying file hash...") as status:
        status.start()
        with open(filename, 'rb') as f:
            filehash_calculated = hashlib.sha256(f.read()).hexdigest()
        status.update()
        time.sleep(0.1)
        if filehash != filehash_calculated:
            raise Exception('File was tampered while downloading!')
        status.stop()
        
    return filename      
    
def uninstall_old_version() -> str:
    pass
    
def install_from_installer(installer_path: str):
    pass

def cleanup(downloaded_installer: str):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update Burp Suite')
    parser.add_argument('-v', '--version', help='Update to version')
    parser.add_argument('-p', '--platform', help='Update for platform [Default Linux]', default='Linux', choices=['Linux', 'LinuxArm64', 'Jar', 'MacOsArm64', 'MaxOsx', 'WindowsX64'])
    parser.add_argument('--download-only', help='Download installer only', action='store_true')
    parser.add_argument('--install-only', help='Install from already downloaded installer only', action='store_true')
    parser.add_argument('--file', help='Path to downloaded archive')
    parser.add_argument('--uninstall-only', help='Uninstall old installation only', action='store_true')
    parser.add_argument('--available-versions', help='Show available versions', action='store_true')
    #parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
    version = get_current_version()
    parser.add_argument('-c', '--current', help='Get current version status', action='version', version=version)

    args = parser.parse_args()
    if not verify_version(args.version, version):
        print(f'Already on version {args.version}')
        exit(0)

    if args.available_versions:
        available_versions = get_available_versions()
        max_len = max([len(version) for version, _ in available_versions])
        print('VERSION\t\tRELEASE CHANNELS')
        for version, channels in available_versions:
            print(f'{version.ljust(max_len)}\t{channels[0]}')
        exit(0)

    if args.download_only:
        try:
            downloaded_installer = download_new_installer(args.version, args.platform)
            print(f'Installer downloaded to {os.getcwd() + "/" + downloaded_installer}')
            exit(0)
        except Exception as e:
            print(f'Error: {e.__str__()}')
            exit(1)

    if args.install_only:
        pass

    if args.uninstall_only:
        pass
        
    try:
        pass
    except Exception as e:
        print(f'Error: {e.__str__()}')
        exit(1)
    
