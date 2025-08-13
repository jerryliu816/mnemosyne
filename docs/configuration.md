# Configuration Guide

This guide covers how to configure the Mnemosyne system, including API keys, network settings, and hardware parameters.

## Overview

All configuration is managed through a single `config.json` file that contains API keys, network settings, hardware parameters, and other configurable options. This approach keeps sensitive information separate from the source code.

## Initial Setup

### Step 1: Create Configuration File

Copy the template to create your configuration file:

```bash
cd /path/to/mnemosyne
cp config.json.template config.json
```

### Step 2: Edit Configuration

Open the configuration file in your preferred editor:

```bash
nano config.json
# or
vim config.json
# or
code config.json
```

## Configuration Sections

### API Keys (Required)

Both server and device require API keys for AI services:

```json
{
  "openai_api_key": "sk-your-openai-api-key-here",
  "google_api_key": "your-google-ai-studio-api-key-here"
}
```

#### Getting OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (starts with `sk-`)
6. **Important:** Keep this key secure and never share it

#### Getting Google AI Studio API Key
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Sign in with your Google account
3. Create a new project or select existing one
4. Navigate to **API Keys** section
5. Click **Create API Key**
6. Copy the generated key
7. **Important:** Keep this key secure

### Network Configuration

Configure server and client network settings:

```json
{
  "contentserver_url": "http://your-server-address:5000/add_content",
  "flask_host": "0.0.0.0",
  "flask_port": 5000,
  "flask_debug": true
}
```

#### Server Settings
- `flask_host`: Server bind address (`0.0.0.0` for all interfaces, `127.0.0.1` for localhost only)
- `flask_port`: Port number for the web server (default: 5000)
- `flask_debug`: Enable debug mode (set to `false` in production)

#### Client Settings
- `contentserver_url`: Complete URL where the Raspberry Pi posts images
- Update the IP address/hostname to match your server location

### Hardware Configuration (Device Only)

GPIO pin assignments and hardware parameters:

```json
{
  "gpio_pins": {
    "openai_button": 3,
    "shutdown_button": 5,
    "google_button": 26,
    "led_1": 12,
    "led_2": 18
  },
  "shutdown_counter_max": 3,
  "camera_temp_path": "/tmp/captured_image.jpg",
  "default_device_id": "default"
}
```

#### GPIO Pin Mapping
- `openai_button`: Button to trigger OpenAI image analysis
- `shutdown_button`: Button for graceful shutdown (requires multiple presses)
- `google_button`: Button to trigger Google Gemini analysis
- `led_1`, `led_2`: Status indicator LEDs

#### Hardware Parameters
- `shutdown_counter_max`: Number of shutdown button presses required
- `camera_temp_path`: Temporary file path for captured images
- `default_device_id`: Default device identifier (will be overridden by IP address)

### AI Model Configuration

Specify which AI models and parameters to use:

```json
{
  "openai_model": "gpt-4o",
  "google_model": "gemini-pro-vision",
  "max_tokens": 1000
}
```

- `openai_model`: OpenAI model for image analysis (gpt-4o, gpt-4-vision-preview)
- `google_model`: Google model for image analysis (gemini-pro-vision)
- `max_tokens`: Maximum tokens in AI responses

### Database Configuration

Database settings for the server:

```json
{
  "database_path": "content_collection.db"
}
```

- `database_path`: SQLite database file path (relative to server directory)

## Complete Configuration Example

Here's a complete `config.json` example:

```json
{
  "openai_api_key": "sk-1234567890abcdef1234567890abcdef1234567890abcdef",
  "google_api_key": "AIzaSyABC123def456GHI789jkl012MNO345pqr678",
  "contentserver_url": "http://192.168.1.100:5000/add_content",
  "database_path": "content_collection.db",
  "flask_host": "0.0.0.0",
  "flask_port": 5000,
  "flask_debug": false,
  "gpio_pins": {
    "openai_button": 3,
    "shutdown_button": 5,
    "google_button": 26,
    "led_1": 12,
    "led_2": 18
  },
  "shutdown_counter_max": 3,
  "camera_temp_path": "/tmp/captured_image.jpg",
  "default_device_id": "pi-camera-01",
  "openai_model": "gpt-4o",
  "google_model": "gemini-pro-vision",
  "max_tokens": 1000
}
```

## Environment-Specific Configuration

### Development Environment

```json
{
  "flask_debug": true,
  "flask_host": "127.0.0.1",
  "contentserver_url": "http://localhost:5000/add_content"
}
```

### Production Environment

```json
{
  "flask_debug": false,
  "flask_host": "0.0.0.0",
  "contentserver_url": "http://your-production-server:5000/add_content"
}
```

## Security Best Practices

### API Key Security
1. **Never commit** `config.json` to version control
2. **Use environment variables** for CI/CD deployments
3. **Rotate keys regularly**
4. **Monitor API usage** for unexpected activity
5. **Use least-privilege access** when possible

### File Permissions
Set appropriate permissions on configuration files:

```bash
# Make config file readable only by owner
chmod 600 config.json

# Verify permissions
ls -l config.json
# Should show: -rw------- (600)
```

### Network Security
1. **Use HTTPS** in production (consider reverse proxy)
2. **Firewall** unnecessary ports
3. **Use VPN** for remote access to Raspberry Pi
4. **Change default passwords** on all devices

## Validation

### Configuration Validation Script

Create a script to validate your configuration:

```python
# validate_config.py
import json
import os
import sys

def validate_config():
    if not os.path.exists('config.json'):
        print("❌ config.json not found")
        return False
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    
    required_keys = [
        'openai_api_key',
        'contentserver_url',
        'database_path',
        'flask_host',
        'flask_port'
    ]
    
    missing_keys = []
    for key in required_keys:
        if key not in config:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing required keys: {', '.join(missing_keys)}")
        return False
    
    # Validate API key format
    if not config['openai_api_key'].startswith('sk-'):
        print("⚠️  OpenAI API key format may be incorrect")
    
    # Validate URL format
    if not config['contentserver_url'].startswith('http'):
        print("⚠️  Content server URL should start with http:// or https://")
    
    print("✅ Configuration validation passed")
    return True

if __name__ == "__main__":
    if validate_config():
        sys.exit(0)
    else:
        sys.exit(1)
```

Run validation:
```bash
python validate_config.py
```

## Troubleshooting

### Common Configuration Issues

1. **Invalid JSON Format:**
   ```bash
   # Check JSON syntax
   python -m json.tool config.json
   ```

2. **Missing API Keys:**
   - Verify keys are correctly copied (no extra spaces)
   - Check key permissions on respective platforms

3. **Network Connection Issues:**
   - Verify server IP address and port
   - Check firewall settings
   - Test connectivity: `curl http://server-ip:5000`

4. **Permission Errors:**
   ```bash
   # Fix file permissions
   chmod 600 config.json
   chown $USER:$USER config.json
   ```

### Debug Mode

Enable debug mode for troubleshooting:

```json
{
  "flask_debug": true
}
```

This provides detailed error messages and auto-reload on code changes.

## Next Steps

After configuration:
1. **Validate** your configuration with the validation script
2. **Test connectivity** between server and device
3. Proceed to [Deployment Guide](deployment.md) to run the applications
4. Check the logs for any configuration-related errors