# Raspberry Pi Hardware Setup Guide

This guide covers the physical setup of the Raspberry Pi, including camera module installation, GPIO wiring for buttons and LEDs, and hardware configuration.

## Required Components

### Core Components
- Raspberry Pi 4 (recommended) or Pi 3B+
- Raspberry Pi Camera Module v2 or v3
- MicroSD card (32GB+ recommended)
- Power supply (USB-C for Pi 4, micro-USB for Pi 3)

### Additional Hardware
- 3x Push buttons (momentary, normally open)
- 2x LEDs (any color, 3mm or 5mm)
- 2x Current limiting resistors (220-330 Ohm for LEDs)
- 3x Pull-up resistors (10k Ohm for buttons) - *Optional if using internal pull-ups*
- Breadboard or perfboard
- Jumper wires (male-to-female and male-to-male)
- Enclosure (optional but recommended)

## Camera Module Installation

### Step 1: Physical Connection
1. **Power down** the Raspberry Pi completely
2. Locate the camera connector between the HDMI and audio jacks
3. **Gently lift** the plastic clip on the camera connector
4. **Insert the ribbon cable** with contacts facing away from the HDMI port
5. **Press down** the plastic clip to secure the cable
6. **Connect the other end** to the camera module (contacts face the PCB)

### Step 2: Enable Camera Interface
```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Select "Yes" and reboot
```

### Step 3: Test Camera
```bash
# Test camera functionality
libcamera-hello --list-cameras
libcamera-still -o test.jpg
```

## GPIO Pin Configuration

The default pin configuration (BOARD numbering):

| Component | GPIO Pin | Physical Pin | Notes |
|-----------|----------|--------------|--------|
| OpenAI Button | GPIO 3 | Pin 5 | Button for OpenAI processing |
| Shutdown Button | GPIO 5 | Pin 29 | Graceful shutdown (3 presses) |
| Google Button | GPIO 26 | Pin 37 | Button for Google Gemini processing |
| LED 1 | GPIO 12 | Pin 32 | Status indicator |
| LED 2 | GPIO 18 | Pin 12 | Status indicator |
| Ground | GND | Pins 6, 9, 14, 20, 25, 30, 34, 39 | Common ground |
| 3.3V Power | 3V3 | Pins 1, 17 | Power for buttons (if needed) |

## Wiring Diagram

### Button Connections
Each button should be wired as follows:

```
[3.3V] ---- [10kΩ resistor] ---- [GPIO Pin] ---- [Button] ---- [GND]
                                      |
                               To Raspberry Pi
```

**Note:** The internal pull-up resistors can be used instead of external ones (software configured).

### LED Connections
Each LED should be wired as follows:

```
[GPIO Pin] ---- [220Ω resistor] ---- [LED Anode] ---- [LED Cathode] ---- [GND]
     |                                   |                   |
To Raspberry Pi                      Long leg            Short leg
```

## Detailed Wiring Instructions

### Button Wiring

1. **OpenAI Button (GPIO 3, Pin 5):**
   - One side of button → GPIO 3 (Pin 5)
   - Other side of button → Ground (Pin 6)
   - Internal pull-up resistor enabled in software

2. **Shutdown Button (GPIO 5, Pin 29):**
   - One side of button → GPIO 5 (Pin 29)
   - Other side of button → Ground (Pin 30)
   - Internal pull-up resistor enabled in software

3. **Google Button (GPIO 26, Pin 37):**
   - One side of button → GPIO 26 (Pin 37)
   - Other side of button → Ground (Pin 39)
   - Internal pull-up resistor enabled in software

### LED Wiring

1. **LED 1 (GPIO 12, Pin 32):**
   - GPIO 12 (Pin 32) → 220Ω resistor → LED anode (long leg)
   - LED cathode (short leg) → Ground (Pin 34)

2. **LED 2 (GPIO 18, Pin 12):**
   - GPIO 18 (Pin 12) → 220Ω resistor → LED anode (long leg)
   - LED cathode (short leg) → Ground (Pin 14)

## Physical Assembly

### Breadboard Layout

```
    Raspberry Pi GPIO Header
    [1]  [2]
    [3]  [4]
    [5]  [6]  ← OpenAI Button to GND
    [7]  [8]
    [9]  [10]
    [11] [12] ← LED 2 connection
    ...
    [29] [30] ← Shutdown Button to GND
    [31] [32] ← LED 1 connection
    [33] [34] ← LED 1 to GND
    [35] [36]
    [37] [38] ← Google Button
    [39] [40] ← Google Button to GND
```

### Enclosure Recommendations

1. **Mounting:**
   - Use standoffs to prevent short circuits
   - Ensure camera ribbon cable has adequate bend radius
   - Leave space for heat dissipation

2. **Access:**
   - Drill holes for LED visibility
   - Ensure buttons are accessible
   - Consider access to GPIO pins for debugging

## Testing Hardware Setup

### GPIO Test Script

Create a test script to verify all connections:

```python
# test_gpio.py
import RPi.GPIO as GPIO
import time

# Configure GPIO
GPIO.setmode(GPIO.BOARD)

# Setup pins
buttons = [5, 29, 37]  # Physical pins for buttons
leds = [32, 12]        # Physical pins for LEDs

# Setup buttons as inputs with pull-up
for button in buttons:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup LEDs as outputs
for led in leds:
    GPIO.setup(led, GPIO.OUT)

try:
    print("Testing LEDs...")
    for led in leds:
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(led, GPIO.LOW)
        time.sleep(0.5)
    
    print("Testing buttons (press each button)...")
    print("Press OpenAI button (Pin 5)...")
    while GPIO.input(5):
        time.sleep(0.1)
    print("OpenAI button pressed!")
    
    print("Press Shutdown button (Pin 29)...")
    while GPIO.input(29):
        time.sleep(0.1)
    print("Shutdown button pressed!")
    
    print("Press Google button (Pin 37)...")
    while GPIO.input(37):
        time.sleep(0.1)
    print("Google button pressed!")
    
    print("All hardware tests passed!")

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
```

Run the test:
```bash
python test_gpio.py
```

## Troubleshooting

### Camera Issues
- **Camera not detected:** Check ribbon cable connections
- **Poor image quality:** Remove lens protective film
- **Connection errors:** Ensure camera interface is enabled

### GPIO Issues
- **Buttons not responding:** Check continuity with multimeter
- **LEDs not lighting:** Verify resistor values and polarity
- **Permission errors:** Add user to gpio group or run with sudo

### Power Issues
- **Unexpected behavior:** Use adequate power supply (3A for Pi 4)
- **Brown-out detection:** Check power supply voltage under load

## Pin Customization

To use different pins, modify the `gpio_pins` section in your `config.json`:

```json
{
  "gpio_pins": {
    "openai_button": 3,
    "shutdown_button": 5,
    "google_button": 26,
    "led_1": 12,
    "led_2": 18
  }
}
```

## Next Steps

After hardware setup:
1. Verify all connections with the test script
2. Proceed to [Configuration Guide](configuration.md)
3. Follow [Deployment Guide](deployment.md) to run the software