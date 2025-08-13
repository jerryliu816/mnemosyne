# Deployment and Running Guide

This guide covers how to run the Mnemosyne system in both development and production environments, including startup procedures, monitoring, and troubleshooting.

## Prerequisites

Before deployment, ensure you have completed:
1. ✅ [Installation Guide](installation.md) - All dependencies installed
2. ✅ [Hardware Setup Guide](hardware-setup.md) - Raspberry Pi wired correctly
3. ✅ [Configuration Guide](configuration.md) - API keys and settings configured

## Development Deployment

### Running the Server (Development)

1. **Navigate to server directory:**
   ```bash
   cd /path/to/mnemosyne/server
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Start the server:**
   ```bash
   python app2.py
   ```

4. **Verify server is running:**
   ```bash
   # Server should display:
   # * Running on all addresses (0.0.0.0)
   # * Running on http://127.0.0.1:5000
   # * Running on http://[your-ip]:5000
   ```

5. **Test web interface:**
   Open browser and navigate to `http://localhost:5000`

### Running the Device (Development)

1. **Navigate to device directory:**
   ```bash
   cd /path/to/mnemosyne/device
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Start the device client:**
   ```bash
   python cam4.py
   ```

4. **Verify device startup:**
   - LEDs should illuminate
   - Console should show \"Querying IP\" message
   - IP address should be displayed

## Production Deployment

### Server Production Setup

#### 1. Using systemd Service

Create a systemd service for the server:

```bash
sudo nano /etc/systemd/system/mnemosyne-server.service
```

```ini
[Unit]
Description=Mnemosyne Server
After=network.target

[Service]
Type=simple
User=your-username
Group=your-group
WorkingDirectory=/path/to/mnemosyne/server
Environment=PATH=/path/to/mnemosyne/server/venv/bin
ExecStart=/path/to/mnemosyne/server/venv/bin/python app2.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mnemosyne-server
sudo systemctl start mnemosyne-server
sudo systemctl status mnemosyne-server
```

#### 2. Using Gunicorn (Recommended)

Install Gunicorn:
```bash
pip install gunicorn
```

Create Gunicorn configuration:
```bash
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

Update systemd service to use Gunicorn:
```ini
ExecStart=/path/to/mnemosyne/server/venv/bin/gunicorn --config gunicorn.conf.py app2:app
```

#### 3. Reverse Proxy with Nginx

Install and configure Nginx:
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/mnemosyne
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Handle large image uploads
    client_max_body_size 10M;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/mnemosyne /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Device Production Setup

#### 1. Using systemd Service

Create a systemd service for the device:

```bash
sudo nano /etc/systemd/system/mnemosyne-device.service
```

```ini
[Unit]
Description=Mnemosyne Camera Device
After=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/mnemosyne/device
Environment=PATH=/home/pi/mnemosyne/device/venv/bin
ExecStart=/home/pi/mnemosyne/device/venv/bin/python cam4.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mnemosyne-device
sudo systemctl start mnemosyne-device
sudo systemctl status mnemosyne-device
```

#### 2. Auto-start on Boot

Add to user's crontab for auto-start:
```bash
crontab -e

# Add this line:
@reboot cd /home/pi/mnemosyne/device && /home/pi/mnemosyne/device/venv/bin/python cam4.py > /tmp/mnemosyne.log 2>&1
```

## Monitoring and Logs

### Server Monitoring

#### Check Service Status
```bash
# SystemD service
sudo systemctl status mnemosyne-server

# View logs
sudo journalctl -u mnemosyne-server -f
```

#### Application Logs
```bash
# If running directly
tail -f /path/to/server/logs/app.log

# Add logging to app2.py
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('mnemosyne-server.log'),
        logging.StreamHandler()
    ]
)
```

### Device Monitoring

#### Check Service Status
```bash
# SystemD service
sudo systemctl status mnemosyne-device

# View logs
sudo journalctl -u mnemosyne-device -f
```

#### Hardware Status
```bash
# Check camera
libcamera-hello --list-cameras

# Check GPIO (install gpiozero)
pip install gpiozero
python -c "from gpiozero import LED; led = LED(18); led.on()"

# Monitor system resources
htop
```

### Log Rotation

Configure log rotation to prevent disk space issues:

```bash
sudo nano /etc/logrotate.d/mnemosyne
```

```
/var/log/mnemosyne/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 your-user your-group
}
```

## Health Checks and Monitoring

### Server Health Check Script

```python
# health_check_server.py
import requests
import sys
import json

def check_server_health():
    try:
        # Load config to get server URL
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        server_url = f"http://localhost:{config['flask_port']}"
        
        # Check if server responds
        response = requests.get(server_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Server health check failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    if check_server_health():
        sys.exit(0)
    else:
        sys.exit(1)
```

### Device Health Check Script

```python
# health_check_device.py
import RPi.GPIO as GPIO
import sys
import json

def check_device_health():
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Check GPIO setup
        GPIO.setmode(GPIO.BOARD)
        
        # Test LED functionality
        led_pin = config['gpio_pins']['led_1']
        GPIO.setup(led_pin, GPIO.OUT)
        GPIO.output(led_pin, GPIO.HIGH)
        GPIO.output(led_pin, GPIO.LOW)
        
        print("✅ Device hardware is healthy")
        return True
        
    except Exception as e:
        print(f"❌ Device health check failed: {e}")
        return False
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    if check_device_health():
        sys.exit(0)
    else:
        sys.exit(1)
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/var/backups/mnemosyne"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/path/to/mnemosyne/server/content_collection.db"

mkdir -p $BACKUP_DIR
sqlite3 $DB_PATH ".backup $BACKUP_DIR/content_collection_$DATE.db"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "content_collection_*.db" -mtime +7 -delete

echo "Database backed up to $BACKUP_DIR/content_collection_$DATE.db"
```

### Configuration Backup

```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/var/backups/mnemosyne/config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp config.json $BACKUP_DIR/config_$DATE.json

echo "Configuration backed up to $BACKUP_DIR/config_$DATE.json"
```

## Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check port availability
sudo netstat -tlnp | grep :5000

# Check configuration
python validate_config.py

# Check permissions
ls -la config.json

# View detailed errors
python app2.py
```

#### Device Won't Connect
```bash
# Test network connectivity
ping your-server-ip

# Check camera
libcamera-hello --list-cameras

# Check GPIO permissions
groups $USER  # Should include 'gpio'

# Test API keys
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  https://api.openai.com/v1/models
```

#### Image Processing Fails
- **Check API quotas** on OpenAI/Google platforms
- **Verify network connectivity** to API endpoints
- **Check image size limits** (resize if necessary)
- **Monitor API rate limits**

### Emergency Procedures

#### Stop All Services
```bash
sudo systemctl stop mnemosyne-server
sudo systemctl stop mnemosyne-device
```

#### Reset Database
```bash
# Backup first!
cp content_collection.db content_collection.db.backup

# Reset database
rm content_collection.db
python -c "from app2 import init_db; init_db()"
```

#### Factory Reset Device
```bash
# Stop service
sudo systemctl stop mnemosyne-device

# Clear logs
sudo rm /var/log/mnemosyne/*

# Reset GPIO
echo "Reboot recommended after factory reset"
```

## Performance Optimization

### Server Optimization
- Use **Gunicorn** with multiple workers
- Enable **database connection pooling**
- Implement **image compression**
- Add **caching** for frequent queries

### Device Optimization
- **Reduce image resolution** if processing is slow
- **Implement local caching** to reduce API calls
- **Optimize GPIO polling** intervals
- **Use hardware acceleration** where available

## Updates and Maintenance

### Update Procedure
```bash
# 1. Backup current installation
./backup_database.sh
./backup_config.sh

# 2. Stop services
sudo systemctl stop mnemosyne-server mnemosyne-device

# 3. Update code (git pull or manual update)
git pull origin main

# 4. Update dependencies
pip install -r requirements-server.txt
pip install -r requirements-device.txt

# 5. Run migrations (if any)
python migrate.py

# 6. Start services
sudo systemctl start mnemosyne-server mnemosyne-device

# 7. Verify functionality
./health_check_server.py
./health_check_device.py
```

This completes the deployment guide. The system should now be fully operational in your chosen environment.