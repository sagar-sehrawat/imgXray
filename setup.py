import os
import platform
import subprocess
import sys

def install_tools():
    os_name = platform.system()
    
    if os_name == 'Linux':
        install_linux_tools()
    elif os_name == 'Darwin':
        install_macos_tools()
    elif os_name == 'Windows':
        install_windows_tools()
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)

def install_linux_tools():
    dist = get_linux_distribution()
    if dist in ['ubuntu', 'debian', 'kali']:
        install_debian_based_tools()
    elif dist in ['redhat', 'fedora', 'centos']:
        install_redhat_based_tools()
    else:
        print(f"Unsupported Linux distribution: {dist}")
        sys.exit(1)

def get_linux_distribution():
    try:
        with open('/etc/os-release') as f:
            os_info = f.read()
            for line in os_info.splitlines():
                if line.startswith('ID='):
                    return line.split('=')[1].strip('"').lower()
    except Exception as e:
        print(f"Failed to determine Linux distribution: {e}")
        sys.exit(1)
    return None

def install_debian_based_tools():
    print("Installing tools for Debian-based Linux...")
    tools = {
        "binwalk": "binwalk",
        "strings": "bsdmainutils",
        "exiftool": "exiftool",
        "zsteg": "zsteg",
    }
    for tool, package in tools.items():
        if not is_tool_installed(package):
            try:
                subprocess.run(['sudo', 'apt-get', 'install', '-y', package], check=True)
                print(f"{tool} installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {tool}: {e}")

def install_redhat_based_tools():
    print("Installing tools for RedHat-based Linux...")
    tools = [
        "binwalk",
        "strings",
        "exiftool",
        "zsteg",
    ]
    for tool in tools:
        if not is_tool_installed(tool):
            try:
                subprocess.run(['sudo', 'yum', 'install', '-y', tool], check=True)
                print(f"{tool} installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {tool}: {e}")

def install_macos_tools():
    print("Installing tools for macOS...")
    tools = [
        "binwalk",
        "strings",
        "exiftool",
        "zsteg",
    ]
    for tool in tools:
        if not is_tool_installed(tool):
            try:
                subprocess.run(['brew', 'install', tool], check=True)
                print(f"{tool} installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {tool}: {e}")

def install_windows_tools():
    print("Installing tools for Windows...")
    tools = {
        'binwalk': 'pip install binwalk',
        'strings': 'choco install strings -y',
        'exiftool': 'choco install exiftool -y',
        'zsteg': 'pip install zsteg',
    }
    for tool, command in tools.items():
        if not is_tool_installed(tool):
            try:
                subprocess.run(command, shell=True, check=True)
                print(f"{tool} installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {tool}: {e}")

def is_tool_installed(tool):
    try:
        result = subprocess.run([tool, '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking if {tool} is installed: {e}")
        return False

if __name__ == '__main__':
    install_tools()
    print("Setup complete. You can now run the main application.")
