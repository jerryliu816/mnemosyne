# Installation Guide

This guide covers installing the necessary packages for both the server and Raspberry Pi device components of the Mnemosyne system.

## Server Requirements

The server component runs the Flask web application and can be deployed on any system with Python 3.7+.

### Python Dependencies

Create a virtual environment and install the required packages:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install server dependencies
pip install flask
pip install openai
pip install requests
pip install sqlite3  # Usually included with Python
```

### Alternative: Requirements File

Create a `requirements-server.txt` file:

```txt
flask>=2.0.0
openai>=1.0.0
requests>=2.25.0
```

Install with:
```bash
pip install -r requirements-server.txt
```

## Raspberry Pi Device Requirements

The device component requires additional hardware-specific libraries for camera and GPIO control.

### System Preparation

1. **Update Raspberry Pi OS:**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Enable Camera Interface:**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → Camera → Enable
   # Reboot when prompted
   ```

### Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install device dependencies
pip install requests
pip install openai
pip install google-generativeai
pip install picamera2
pip install pillow
pip install RPi.GPIO
```

### Alternative: Requirements File

Create a `requirements-device.txt` file:

```txt
requests>=2.25.0
openai>=1.0.0
google-generativeai>=0.3.0
picamera2>=0.3.0
pillow>=8.0.0
RPi.GPIO>=0.7.0
```

Install with:
```bash
pip install -r requirements-device.txt
```

### System Libraries

Install additional system libraries that may be required:

```bash
# Camera and image processing libraries
sudo apt install -y python3-picamera2
sudo apt install -y python3-libcamera
sudo apt install -y python3-kms++

# Development tools (if needed)
sudo apt install -y python3-dev
sudo apt install -y libffi-dev
sudo apt install -y libjpeg-dev
sudo apt install -y zlib1g-dev
```

## Verification

### Server Verification

Test that the server dependencies are properly installed:

```python
# test_server.py
try:
    import flask
    import openai
    import requests
    import sqlite3
    print("✓ All server dependencies installed successfully")
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
```

### Device Verification

Test that the device dependencies are properly installed:

```python
# test_device.py
try:
    import requests
    import openai
    import google.generativeai as genai
    from picamera2 import Picamera2
    from PIL import Image
    import RPi.GPIO as GPIO
    print("✓ All device dependencies installed successfully")
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
```

## Troubleshooting

### Common Issues

1. **Permission Errors on Raspberry Pi:**
   ```bash
   sudo usermod -a -G video $USER
   sudo usermod -a -G gpio $USER
   # Log out and back in
   ```

2. **Camera Not Detected:**
   ```bash
   # Check if camera is detected
   libcamera-hello --list-cameras
   
   # If not detected, check connections and enable legacy camera support
   sudo raspi-config
   # Advanced Options → GL Driver → Legacy
   ```

3. **GPIO Permission Issues:**
   ```bash
   # Add user to gpio group
   sudo usermod -a -G gpio $USER
   
   # Or run with sudo (not recommended for production)
   sudo python cam4.py
   ```

4. **Virtual Environment Issues:**
   ```bash
   # If venv creation fails
   sudo apt install python3-venv
   
   # If pip is missing
   sudo apt install python3-pip
   ```

## Next Steps

After installation, proceed to:
1. [Hardware Setup Guide](hardware-setup.md) - For Raspberry Pi wiring
2. [Configuration Guide](configuration.md) - For API keys and settings
3. [Deployment Guide](deployment.md) - For running the applications