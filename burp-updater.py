#!/usr/bin/env python3
import os
import argparse
import hashlib
import requests
import subprocess
import traceback

from rich.console import Console
from rich.progress import Progress
import time

API_URL = "https://portswigger.net/burp/releases/data"
DOWNLOAD_URL = "https://portswigger-cdn.net/burp/releases/download?product=community"
DEFAULT_INSTALLATION_DIR = "/opt/BurpSuiteCommunity"


def get_current_version() -> str:
    try:
        version = (
            subprocess.run(["BurpSuiteCommunity", "--version"], capture_output=True)
            .stdout.decode("utf-8")
            .split(" ")[0]
        )
    except FileNotFoundError:
        version = ""
    return version.split("-")[0]


def verify_version(version: str, current_version: str) -> bool:
    burp_exists = (
        subprocess.run(["which", "BurpSuiteCommunity"], capture_output=True).returncode
        == 0
    )
    if burp_exists:
        return version != current_version
    return True


def compare_versions(version1: str, version2: str) -> int:
    version1 = version1.split(".")
    version2 = version2.split(".")
    for i in range(len(version1)):
        if int(version1[i]) > int(version2[i]):
            return 1
        elif int(version1[i]) < int(version2[i]):
            return -1
    return 0


def get_available_versions() -> list:
    console = Console()
    with console.status("[bold green]Fetching available versions...") as status:
        try:
            status.start()
            result_set = requests.get(API_URL + "?pageSize=500").json()["ResultSet"]
            results = result_set["Results"]
            versions = []
            for result in results:
                if (
                    result["productType"] != "pro"
                    or result["productType"] != "enterprise"
                ):
                    versions.append((result["version"], result["releaseChannels"]))
            time.sleep(0.1)
            status.update()
            return versions
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return None
        finally:
            status.stop()


def check_for_updates(current_version: str) -> tuple:
    console = Console()
    with console.status("[bold green]Fetching available versions...") as status:
        try:
            status.start()
            result_set = requests.get(API_URL + "?pageSize=2").json()["ResultSet"]
            results = result_set["Results"]
            for result in results:
                if (
                    result["productType"] != "pro"
                    and result["productType"] != "enterprise"
                ) and result["releaseChannels"][0] == "Stable":
                    comp = compare_versions(current_version, result["version"])
                    if comp == -1:
                        versions = (result["version"], result["releaseChannels"])
                        break
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
        result_set = requests.get(API_URL + "?pageSize=500").json()["ResultSet"]
        results = result_set["Results"]
        for result in results:
            if result["version"] == version:
                builds = result["builds"]
                break
        for build in builds:
            if (
                build["ProductId"] == "community"
                and build["ProductPlatform"] == platform
                and build["Version"] == version
            ):
                filename = (
                    "burpsuite_community_"
                    + platform.lower()
                    + "_v"
                    + version.replace(".", "_")
                    + ".sh"
                )
                filehash = build["Sha256Checksum"]
                break
        status.update()
        time.sleep(0.1)
        status.stop()
    response_headers = requests.head(DOWNLOAD_URL + f"&version={version}&type={platform}").headers
    file_size = int(response_headers.get("Content-Length", 0))
    with requests.get(
        DOWNLOAD_URL + f"&version={version}&type={platform}", stream=True
    ) as r:
        r.raise_for_status()
        progress = Progress()
        with Progress() as progress:
            task = progress.add_task(
                f"[cyan]Downloading {filename}...", total=file_size, start=True
            )
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))
            progress.stop()

    with console.status("[bold green]Verifying file hash...") as status:
        status.start()
        with open(filename, "rb") as f:
            filehash_calculated = hashlib.sha256(f.read()).hexdigest()
        status.update()
        time.sleep(0.1)
        if filehash != filehash_calculated:
            raise Exception("File was tampered while downloading!")
        status.stop()

    return filename


def uninstall_old_version() -> str:
    dir_to_remove = DEFAULT_INSTALLATION_DIR
    prompt = input(f"Is your old installation at {DEFAULT_INSTALLATION_DIR}? [y/N]: ")
    if not prompt.lower() in ["y", "yes"]:
        dir_to_remove = input("Enter path to old installation: ")
    print(
        f"WARNING: The following directory and contents will be removed: {dir_to_remove}..."
    )
    prompt = input("Proceed further? [y/N]: ")
    if not os.path.exists(dir_to_remove + "/uninstall"):
        raise Exception(
            f'Specified uninstaller({dir_to_remove + "/uninstall"}) does not exist!'
        )
    if not prompt.lower() in ["y", "yes"]:
        return
    if os.geteuid() != 0:
        process = subprocess.run(
            ["bash", "-c", f'sudo bash {dir_to_remove + "/uninstall"}'],
            capture_output=True,
            check=True,
        )
        if process.returncode != 0:
            raise Exception("Unable to remove old installation")
    else:
        process = subprocess.run(
            ["bash", "-c", f'bash {dir_to_remove + "/uninstall"}'],
            capture_output=True,
            check=True,
        )
        if process.returncode != 0:
            raise Exception("Unable to remove old installation")
    print("Old installation removed!!!")
    return dir_to_remove


def install_from_installer(installer_path: str):
    if os.geteuid() != 0:
        process = subprocess.run(
            ["bash", "-c", f"sudo bash {installer_path}"],
            capture_output=True,
            check=True,
        )
        if process.returncode != 0:
            raise Exception("An error occured while installing!")
    else:
        process = subprocess.run(
            ["bash", "-c", f"bash {installer_path}"], capture_output=True, check=True
        )
        if process.returncode != 0:
            raise Exception("An error occured while installing!")
    print("New version installed successfully")


def cleanup(downloaded_installer: str):
    try:
        os.remove(downloaded_installer)
    except Exception as e:
        raise Exception(f"Error while removing downloaded installer: {e.__str__()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Burp Suite Community Edition")
    parser.add_argument("-v", "--version", help="Update to version")
    parser.add_argument(
        "-p",
        "--platform",
        help="Update for platform [Default Linux]",
        default="Linux",
        choices=["Linux", "LinuxArm64", "Jar", "MacOsArm64", "MaxOsx"],
    )
    parser.add_argument(
        "--download-only", help="Download installer only", action="store_true"
    )
    parser.add_argument(
        "--install-only",
        help="Install from already downloaded installer only",
        action="store_true",
    )
    parser.add_argument("--file", help="Path to downloaded installer")
    parser.add_argument(
        "--uninstall-only", help="Uninstall old installation only", action="store_true"
    )
    parser.add_argument(
        "--available-versions", help="Show available versions", action="store_true"
    )
    parser.add_argument("--check", help="Check for updates", action="store_true")
    # parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
    version = get_current_version()
    parser.add_argument(
        "-c",
        "--current",
        help="Get current version status",
        action="version",
        version=version,
    )

    args = parser.parse_args()
    if not verify_version(args.version, version):
        print(f"Already on version {args.version}")
        exit(0)

    if args.available_versions:
        available_versions = get_available_versions()
        max_len = max([len(version) for version, _ in available_versions])
        print("VERSION\t\tRELEASE CHANNELS")
        for version, channels in available_versions:
            print(f"{version.ljust(max_len)}\t{channels[0]}")
        exit(0)

    if args.download_only:
        try:
            downloaded_installer = download_new_installer(args.version, args.platform)
            print(f'Installer downloaded to {os.getcwd() + "/" + downloaded_installer}')
            exit(0)
        except Exception as e:
            print(f"Error: {e.__str__()}")
            exit(1)

    if args.check:
        versions = check_for_updates(version)
        if len(versions) == 0:
            print("No updates available!")
            exit(0)
        print("Updates available!!!")
        print(f"Version: {versions[0]} | Release Channels: {versions[1][0]}")
        exit(0)

    if args.install_only:
        if not args.file:
            parser.error("--install-only requires --file [INSTALLER]")
        install_from_installer(args.file)
        exit(0)

    if args.uninstall_only:
        try:
            uninstall_old_version()
            process = subprocess.run(["bash", "-c", "sudo -k"], check=True)
            if process.returncode != 0:
                raise Exception()
        except:
            print("Unable to uninstall old version")
            exit(1)
        finally:
            exit(0)

    try:
        downloaded_archive = download_new_installer(args.version, args.platform)
        print(f'Installer downloaded to {os.getcwd() + "/" + downloaded_archive}')
        uninstall_old_version()
        install_from_installer(downloaded_archive)
        proc = subprocess.run(["bash", "-c", "sudo -k"], check=True)
        if proc.returncode != 0:
            raise Exception("Error while dropping sudo privileges")
        print("Cleaning up...")
        cleanup(downloaded_archive)
    except Exception as e:
        # print(f'Error: {e.__str__()}')
        traceback.print_exc()
        exit(1)
