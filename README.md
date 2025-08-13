# Mnemosyne - Visual Memory System

[![License](https://img.shields.io/badge/license-AGPL%203.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![Raspberry Pi](https://img.shields.io/badge/raspberry%20pi-4%2F3B+-red.svg)](https://raspberrypi.org)

Mnemosyne is an intelligent visual memory system that combines IoT camera devices with AI-powered scene analysis to create a searchable database of visual memories. The system captures images through Raspberry Pi cameras, processes them using advanced AI vision models, and provides natural language querying capabilities.

![Mnemosyne System Overview](docs/assets/system-diagram.png)

## ✨ Features

### 🤖 AI-Powered Analysis
- **Dual AI Support**: OpenAI GPT-4 Vision and Google Gemini Pro Vision
- **Intelligent Scene Description**: Automatic object detection and scene understanding
- **Natural Language Queries**: Ask questions about stored memories in plain English

### 📷 IoT Camera Integration
- **Raspberry Pi Camera Support**: PiCamera2 integration with auto-exposure
- **GPIO Hardware Controls**: Physical buttons for different AI services
- **LED Status Indicators**: Visual feedback for device status
- **Graceful Shutdown**: Multi-press shutdown protection

### 🌐 Web Interface
- **Content Management**: View, filter, and delete stored memories
- **Date/Time Filtering**: Search memories by specific time ranges
- **Image Gallery**: Optional image display in management interface
- **Query Interface**: Natural language search with visual results

### 🔒 Security & Configuration
- **External Configuration**: API keys and settings in separate config files
- **Git-Safe**: Sensitive information excluded from version control
- **Flexible Deployment**: Development and production configurations

## 🏗️ System Architecture

```
┌─────────────────┐    HTTP POST     ┌─────────────────┐
│                 │   /add_content   │                 │
│  Raspberry Pi   ├─────────────────▶│  Flask Server   │
│  Camera Device  │                  │  (Content Mgmt) │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
        │                                      │
        │                                      │
    ┌───▼────┐                            ┌────▼────┐
    │ PiCam2 │                            │ SQLite  │
    │ + GPIO │                            │Database │
    └────────┘                            └─────────┘
        │                                      │
    ┌───▼────┐                            ┌────▼────┐
    │OpenAI/ │                            │   Web   │
    │Gemini  │                            │Interface│
    │   API  │                            │         │
    └────────┘                            └─────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Server**: Any system with Python 3.7+
- **Device**: Raspberry Pi 4 (recommended) or 3B+
- **APIs**: OpenAI API key, Google AI Studio key
- **Hardware**: Camera module, buttons, LEDs, resistors

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jerryliu816/mnemosyne.git
   cd mnemosyne
   ```

2. **Set up configuration**
   ```bash
   cp config.json.template config.json
   # Edit config.json with your API keys and settings
   ```

3. **Install dependencies**
   
   **Server:**
   ```bash
   cd server
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install flask openai requests
   ```
   
   **Device:**
   ```bash
   cd device
   python -m venv venv
   source venv/bin/activate
   pip install requests openai google-generativeai picamera2 pillow RPi.GPIO
   ```

4. **Run the system**
   
   **Start Server:**
   ```bash
   cd server
   python app2.py
   # Server available at http://localhost:5000
   ```
   
   **Start Device:**
   ```bash
   cd device
   python cam4.py
   # Device ready - press buttons to capture images
   ```

### Hardware Setup

Connect components to Raspberry Pi GPIO pins:

| Component | Default Pin | Description |
|-----------|------------|-------------|
| OpenAI Button | GPIO 3 | Triggers OpenAI image analysis |
| Shutdown Button | GPIO 5 | Graceful shutdown (3 presses) |
| Google Button | GPIO 26 | Triggers Google Gemini analysis |
| LED 1 | GPIO 12 | Primary status indicator |
| LED 2 | GPIO 18 | Secondary status indicator |

See [Hardware Setup Guide](docs/hardware-setup.md) for detailed wiring instructions.

## 📖 Documentation

### Setup Guides
- 📋 [Installation Guide](docs/installation.md) - Dependencies and system setup
- 🔌 [Hardware Setup](docs/hardware-setup.md) - GPIO wiring and camera installation
- ⚙️ [Configuration Guide](docs/configuration.md) - API keys and settings
- 🚀 [Deployment Guide](docs/deployment.md) - Running in production

### API Reference
- 🔗 [Server API Documentation](docs/api-reference.md) - REST endpoints and payloads
- 🎛️ [Configuration Schema](docs/configuration-schema.md) - Complete config options

## 🎯 Use Cases

### 🏠 Home Monitoring
- **Security**: Monitor entry points and detect unusual activity
- **Pet Tracking**: Keep track of pet activities and behaviors
- **Child Safety**: Monitor play areas and outdoor activities

### 🏢 Business Applications
- **Retail Analytics**: Customer behavior and traffic patterns
- **Workspace Monitoring**: Meeting room usage and occupancy
- **Inventory Tracking**: Visual verification of stock levels

### 🔬 Research & Development
- **Behavior Studies**: Animal or human behavior analysis
- **Environmental Monitoring**: Time-lapse environmental changes
- **Prototype Testing**: Visual documentation of experiments

## 💬 Example Queries

Once your system is capturing images, you can ask natural language questions:

- *"What activities happened in the kitchen between 2 PM and 4 PM?"*
- *"Were there any people in the living room today?"*
- *"What changes occurred in the backyard throughout the day?"*
- *"When was the last time someone was at the front door?"*
- *"Show me all scenes with pets or animals"*

## 🛠️ API Reference

### POST /add_content
Receive images from camera devices.

```json
{
  "image": "base64-encoded-jpeg-data",
  "description": "optional-description",
  "deviceid": "device-identifier"
}
```

**Response:**
```json
{
  "message": "Content added successfully"
}
```

### GET /get_contents
Retrieve all stored content as JSON.

### GET/POST /contents
Web interface for content management with filtering and deletion.

### GET/POST /query
Natural language query interface with date/time filtering.

## 🔧 Configuration

### Essential Settings

```json
{
  "openai_api_key": "sk-your-key-here",
  "google_api_key": "your-google-key-here",
  "contentserver_url": "http://your-server:5000/add_content",
  "gpio_pins": {
    "openai_button": 3,
    "shutdown_button": 5,
    "google_button": 26,
    "led_1": 12,
    "led_2": 18
  }
}
```

### Security Best Practices
- ✅ Keep `config.json` out of version control
- ✅ Use environment variables in production
- ✅ Rotate API keys regularly
- ✅ Monitor API usage for anomalies

## 🚦 System Requirements

### Server Requirements
- **OS**: Linux, macOS, Windows
- **Python**: 3.7 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 10GB+ (depending on image storage needs)
- **Network**: Stable internet connection for AI APIs

### Device Requirements
- **Hardware**: Raspberry Pi 4 (recommended) or 3B+
- **OS**: Raspberry Pi OS (Bullseye or newer)
- **Camera**: Pi Camera Module v2 or v3
- **Storage**: 32GB+ microSD card
- **Network**: Wi-Fi or Ethernet connection

## 🧪 Development

### Setting Up Development Environment

1. **Fork and clone** the repository
2. **Create virtual environments** for both server and device
3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```
4. **Run tests**
   ```bash
   pytest tests/
   ```

### Code Structure
```
mnemosyne/
├── server/              # Flask web application
│   ├── app2.py         # Main server application
│   └── config.json     # Server configuration
├── device/             # Raspberry Pi camera client
│   ├── cam4.py         # Camera device application
│   └── config.json     # Device configuration
├── docs/               # Documentation
├── tests/              # Test suite
└── config.json.template # Configuration template
```

### Contributing Guidelines
1. **Fork** the repository
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make changes** with clear commit messages
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

## 📈 Performance

### Typical Performance Metrics
- **Image Capture**: ~2-3 seconds per image
- **AI Processing**: 3-5 seconds (OpenAI), 2-4 seconds (Google)
- **Database Storage**: ~1MB per image (depending on resolution)
- **Query Response**: <1 second for text queries, 2-5 seconds with AI analysis

### Optimization Tips
- **Reduce image resolution** for faster processing
- **Use server-side AI processing** to reduce device load
- **Implement local caching** to reduce API calls
- **Use SSD storage** for better database performance

## 🐛 Troubleshooting

### Common Issues

**Camera not detected:**
```bash
libcamera-hello --list-cameras
sudo raspi-config  # Enable camera interface
```

**GPIO permission errors:**
```bash
sudo usermod -a -G gpio $USER
# Log out and back in
```

**API key errors:**
- Verify keys are correctly set in config.json
- Check API quotas and billing status
- Test connectivity to AI service endpoints

**Server connection failures:**
- Verify server IP address and port
- Check firewall settings
- Test with: `curl http://server-ip:5000`

See [Troubleshooting Guide](docs/troubleshooting.md) for detailed solutions.

## 📊 Monitoring & Analytics

### Built-in Monitoring
- **Server Logs**: Request/response logging with timestamps
- **Device Status**: GPIO status and camera health checks
- **API Usage**: Track AI service usage and costs
- **Database Growth**: Monitor storage usage over time

### Health Checks
```bash
# Server health check
curl http://localhost:5000/health

# Device hardware test
python test_gpio.py
```

## 🔒 Privacy & Security

### Data Protection
- **Local Storage**: Images stored locally by default
- **API Transmission**: Images sent to AI services for processing
- **Data Retention**: Configure automatic cleanup policies
- **Access Control**: Web interface access controls

### Privacy Considerations
- **Inform stakeholders** about camera monitoring
- **Comply with local laws** regarding surveillance
- **Implement data retention** policies
- **Consider edge processing** for sensitive environments

## 📜 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

### License Summary
The AGPL-3.0 license ensures that:
- ✅ **Freedom to use** - Use the software for any purpose
- ✅ **Freedom to study** - Access to source code and documentation
- ✅ **Freedom to modify** - Make changes and improvements
- ✅ **Freedom to distribute** - Share with others under the same license
- 🔒 **Network copyleft** - If you run this software as a service, you must provide source code to users

This license is specifically chosen to ensure that improvements to Mnemosyne benefit the entire community, even when deployed as a web service.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Code standards and style guidelines
- Testing requirements
- Documentation standards
- Pull request process

## 💡 Roadmap

### Upcoming Features
- [ ] **Edge AI Processing**: Local AI models for offline operation
- [ ] **Multi-device Support**: Centralized management of multiple cameras
- [ ] **Advanced Analytics**: Object tracking and behavior analysis
- [ ] **Mobile App**: iOS/Android companion app
- [ ] **Cloud Storage**: Optional cloud storage integration
- [ ] **Real-time Alerts**: Notification system for specific events

### Long-term Goals
- [ ] **Facial Recognition**: Privacy-aware face detection and recognition
- [ ] **Voice Integration**: Voice commands and audio analysis
- [ ] **AR Visualization**: Augmented reality scene reconstruction
- [ ] **Machine Learning**: Custom model training on local data

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 Vision API
- **Google** for Gemini Pro Vision API
- **Raspberry Pi Foundation** for excellent hardware and documentation
- **PiCamera2** team for the modern camera interface
- **Flask** community for the web framework
- **Contributors** who help improve this project

## 📞 Support

### Getting Help
- 📚 [Documentation](docs/) - Comprehensive setup and usage guides
- 🐛 [Issues](https://github.com/jerryliu816/mnemosyne/issues) - Bug reports and feature requests
- 💬 [Discussions](https://github.com/jerryliu816/mnemosyne/discussions) - Community support and ideas
- 📧 [Email](mailto:support@mnemosyne-project.com) - Direct support for enterprise users

### Community
- 🌟 **Star this repo** if you find it useful
- 🍴 **Fork and contribute** to help improve the project
- 📢 **Share your use cases** and experiences
- 🎥 **Create tutorials** and guides for the community

---

**Made with ❤️ by the Mnemosyne Project**

*Transform your visual memories into searchable intelligence.*