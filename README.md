# BurpSuite-Community-Updater

- As you all non-Parrot/Kali/BlackArch webapp testers know that `BurpSuite` can't be added to package repositories, hence we need to update it manually everytime. This script will help to automate that process.

- You can also download only, or install from an installer or even uninstall the previous installation only.
- How to use:

```
→ python3 burp-updater.py --help
usage: burp-updater.py [-h] [-v VERSION] [-p {Linux,LinuxArm64,Jar,MacOsArm64,MaxOsx,WindowsX64}] [--download-only]
                       [--install-only] [--file FILE] [--uninstall-only] [--available-versions] [--check] [-c]

Update Burp Suite Community Edition

options:
  -h, --help            show this help message and exit
  -v VERSION, --version VERSION
                        Update to version
  -p {Linux,LinuxArm64,Jar,MacOsArm64,MaxOsx}, --platform {Linux,LinuxArm64,Jar,MacOsArm64,MaxOsx}
                        Update for platform [Default Linux]
  --download-only       Download installer only
  --install-only        Install from already downloaded installer only
  --file FILE           Path to downloaded installer
  --uninstall-only      Uninstall old installation only
  --available-versions  Show available versions
  --check               Check for updates
  -c, --current         Get current version status
```

- Installation:
  ```
  git clone https://github.com/The-Debarghya/burp-updater
  pip3 install -r requirements.txt
  ```

- Currently supports ONLY `Community Edition` of Burp in Linux and Mac only.