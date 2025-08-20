#!/usr/bin/env python3
"""
Setup script for Speech-to-Text Recorder

This script helps with the initial setup and installation of dependencies.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_system_dependencies():
    """Install system-level dependencies."""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("🍎 Detected macOS")
        # Check if Homebrew is available
        if subprocess.run("which brew", shell=True, capture_output=True).returncode == 0:
            return run_command("brew install portaudio", "Installing PortAudio via Homebrew")
        else:
            print("⚠️  Homebrew not found. Please install PortAudio manually:")
            print("   brew install portaudio")
            return False
            
    elif system == "linux":
        print("🐧 Detected Linux")
        # Try apt-get first (Ubuntu/Debian)
        if subprocess.run("which apt-get", shell=True, capture_output=True).returncode == 0:
            return run_command("sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-pyaudio", 
                             "Installing PortAudio via apt-get")
        # Try yum (CentOS/RHEL)
        elif subprocess.run("which yum", shell=True, capture_output=True).returncode == 0:
            return run_command("sudo yum install -y portaudio-devel", 
                             "Installing PortAudio via yum")
        else:
            print("⚠️  Package manager not detected. Please install PortAudio manually.")
            return False
            
    elif system == "windows":
        print("🪟 Detected Windows")
        print("ℹ️  Windows dependencies should install automatically with pip")
        return True
    
    else:
        print(f"⚠️  Unknown system: {system}")
        return False

def install_python_dependencies():
    """Install Python dependencies."""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                      "Installing Python dependencies")

def test_installation():
    """Test if the installation works."""
    print("🧪 Testing installation...")
    
    # Test imports
    try:
        import sounddevice
        print("✅ sounddevice imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import sounddevice: {e}")
        return False
    
    try:
        import whisper
        print("✅ whisper imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import whisper: {e}")
        return False
    
    try:
        import pynput
        print("✅ pynput imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pynput: {e}")
        return False
    
    # Test Whisper model loading
    try:
        print("🔄 Testing Whisper model download...")
        model = whisper.load_model("tiny")
        print("✅ Whisper tiny model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load Whisper model: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Speech-to-Text Recorder Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install system dependencies
    print("\n📦 Installing system dependencies...")
    if not install_system_dependencies():
        print("⚠️  System dependency installation failed. You may need to install manually.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Install Python dependencies
    print("\n🐍 Installing Python dependencies...")
    if not install_python_dependencies():
        print("❌ Python dependency installation failed")
        sys.exit(1)
    
    # Test installation
    print("\n🧪 Testing installation...")
    if test_installation():
        print("\n🎉 Setup completed successfully!")
        print("\nYou can now run the application:")
        print("   python main.py              # GUI mode")
        print("   python main.py --headless   # Headless mode")
        print("   python main.py --help       # Show help")
    else:
        print("\n❌ Setup completed with errors. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
