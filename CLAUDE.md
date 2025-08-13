# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mnemosyne is a visual memory system consisting of two main components:

1. **Flask Web Server** (`app2.py`) - Content management server that:
   - Receives and stores base64-encoded images with AI-generated descriptions
   - Uses OpenAI GPT-4o for image analysis and scene understanding
   - Provides web interface for viewing, managing, and querying stored content
   - Stores data in SQLite database (`content_collection.db`)

2. **Raspberry Pi Camera Client** (`cam4.py`) - IoT device that:
   - Captures images using PiCamera2 on Raspberry Pi
   - Uses GPIO buttons for triggering different AI services (OpenAI GPT-4o or Google Gemini)
   - Posts captured images to the Flask server for processing and storage
   - Includes LED indicators and graceful shutdown functionality

## Architecture

- **Database**: SQLite with `content` table storing: id, image (base64), description, timestamp, deviceid
- **AI Integration**: Dual support for OpenAI GPT-4o and Google Gemini Pro Vision
- **Camera Integration**: PiCamera2 library for Raspberry Pi camera module
- **Web Interface**: Flask with Bootstrap styling for content management
- **Hardware Interface**: GPIO controls for buttons (pins 3, 5, 26) and LEDs (pins 12, 18)

## Setup and Configuration

### Initial Setup
1. Copy the configuration template:
   ```bash
   cp config.json.template config.json
   ```

2. Edit `config.json` with your API keys and settings:
   - `openai_api_key`: Your OpenAI API key
   - `google_api_key`: Your Google AI Studio API key (for device only)
   - `contentserver_url`: URL where the camera device posts images
   - Other settings can be customized as needed

### Development Commands

#### Running the Flask Server
```bash
cd server
python app2.py
```
Server configuration (host, port, debug mode) is controlled via `config.json`.

#### Running the Pi Camera Client
```bash
cd device
python cam4.py
```
Requires Raspberry Pi hardware with camera module and GPIO setup.

## Key Components

### Flask Routes
- `/` - Home page with navigation links
- `/add_content` (POST) - Accepts JSON with image, description, deviceid
- `/get_contents` (GET) - Returns JSON of all stored content
- `/contents` (GET/POST) - Web interface for viewing/deleting content with date filtering
- `/query` (GET/POST) - Natural language querying of stored scenes using GPT-4

### Camera Functions
- `capture_image_and_save_to_base64()` - Main image capture function
- `captureImageOpenai()` - Capture and process with OpenAI (GPIO pin 3)
- `captureImageGoogle()` - Capture and process with Google Gemini (GPIO pin 26)
- Button on GPIO pin 5 initiates graceful shutdown sequence

## Configuration

### Configuration File Structure
All sensitive information and configurable parameters are stored in `config.json`. Key settings include:

- **API Keys**: OpenAI and Google AI Studio API keys
- **Network**: Content server URL, Flask host/port settings  
- **Hardware**: GPIO pin assignments for buttons and LEDs
- **AI Models**: Model names and token limits
- **Paths**: Database path, camera temp file location

### Security
- `config.json` is excluded from version control via `.gitignore`
- Use `config.json.template` as a reference for required settings
- Never commit actual API keys to the repository

### Hardware Requirements (device/cam4.py)
- Raspberry Pi with camera module
- GPIO buttons (configurable pins, defaults: 3, 5, 26)
- LEDs (configurable pins, defaults: 12, 18)
- Network connectivity for posting to content server

## Database Schema
```sql
CREATE TABLE content (
    id INTEGER PRIMARY KEY,
    image TEXT,           -- base64 encoded image
    description TEXT,     -- AI-generated description
    timestamp TEXT,       -- YYYY-MM-DD HH:MM:SS format
    deviceid TEXT        -- device identifier (IP address for Pi client)
);
```