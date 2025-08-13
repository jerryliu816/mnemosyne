# Mnemosyne Documentation

Complete setup and deployment documentation for the Mnemosyne visual memory system.

## Quick Start

1. **[Installation Guide](installation.md)** - Install Python packages and system dependencies
2. **[Hardware Setup Guide](hardware-setup.md)** - Wire Raspberry Pi camera, buttons, and LEDs  
3. **[Configuration Guide](configuration.md)** - Set up API keys and system settings
4. **[Deployment Guide](deployment.md)** - Run the system in development or production

## System Overview

Mnemosyne is a visual memory system consisting of:

- **Flask Web Server** - Content management with AI-powered scene analysis
- **Raspberry Pi Camera Device** - IoT camera client with GPIO controls
- **Dual AI Integration** - OpenAI GPT-4o and Google Gemini Pro Vision support

## Documentation Structure

### 📋 [Installation Guide](installation.md)
- Server and device Python dependencies
- Raspberry Pi system libraries
- Camera interface setup
- Verification scripts

### 🔌 [Hardware Setup Guide](hardware-setup.md)  
- Camera module installation
- GPIO wiring diagrams
- Button and LED connections
- Hardware testing procedures

### ⚙️ [Configuration Guide](configuration.md)
- API key setup (OpenAI & Google)
- Network configuration
- Hardware parameter tuning
- Security best practices

### 🚀 [Deployment Guide](deployment.md)
- Development environment setup
- Production deployment with systemd
- Monitoring and logging
- Backup and recovery procedures

## Prerequisites

- **Server**: Any system with Python 3.7+ 
- **Device**: Raspberry Pi 4 (recommended) or Pi 3B+
- **Accounts**: OpenAI API account, Google AI Studio account
- **Hardware**: Camera module, buttons, LEDs, resistors, wiring

## Support

For issues and questions:
- Check the troubleshooting sections in each guide
- Review the main [CLAUDE.md](../CLAUDE.md) file for technical details
- Verify your hardware connections and configuration

## Next Steps

Start with the [Installation Guide](installation.md) to begin setting up your Mnemosyne system.