#!/usr/bin/env python3
"""
Mnemosyne Camera Device Client

This Raspberry Pi camera client captures images using the PiCamera2 library and processes
them through AI vision services (OpenAI GPT-4 Vision or Google Gemini Pro Vision).
The processed images and descriptions are sent to the Mnemosyne server for storage
and future querying.

Hardware Features:
- PiCamera2 integration for image capture
- GPIO button controls for different AI services
- LED status indicators for visual feedback
- Graceful shutdown mechanism with multi-press detection

AI Integration:
- OpenAI GPT-4 Vision API for detailed scene analysis
- Google Gemini Pro Vision API for alternative analysis
- Configurable processing: local AI calls or server-side processing

Network Features:
- Automatic IP address detection for device identification  
- HTTP POST requests to Mnemosyne server
- Error handling and retry capabilities

GPIO Configuration (configurable via config.json):
- Button 1 (default GPIO 3): Trigger OpenAI image analysis
- Button 2 (default GPIO 5): Graceful shutdown (requires multiple presses)
- Button 3 (default GPIO 26): Trigger Google Gemini analysis
- LED 1 (default GPIO 12): Primary status indicator
- LED 2 (default GPIO 18): Secondary status indicator

Author: Mnemosyne Project
License: See project documentation
"""

import base64
import requests
import time
import libcamera
import os
import json
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import google.generativeai as genai
import socket
import sys
from io import BytesIO
from picamera2 import Picamera2
from PIL import Image

def load_config():
    """
    Load configuration from config.json file.
    
    This function loads the device configuration including API keys,
    GPIO pin assignments, network settings, and AI model parameters.
    
    Returns:
        dict: Configuration dictionary loaded from config.json
        
    Exits:
        System exit with code 1 if config.json is not found
        
    Raises:
        json.JSONDecodeError: If config.json contains invalid JSON
        IOError: If config.json cannot be read
    """
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"Config file {config_path} not found. Please copy config.json.template to config.json and configure it.")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)

# Global configuration and state variables
config = load_config()
shutdownCounter = config['shutdown_counter_max']  # Counter for graceful shutdown
picam2 = None  # PiCamera2 instance (initialized on first use)
devId = config['default_device_id']  # Device identifier (will be overridden by IP)
ip = ""  # Device IP address (detected at runtime)
firstTime = 0  # Flag for first-time initialization

def buttonCallback(channel):
    """
    GPIO callback for OpenAI button press (default GPIO 3).
    
    This function is triggered when the OpenAI button is pressed. It:
    1. Sets LED status indicators
    2. Resets shutdown counter
    3. Triggers image capture and OpenAI processing
    
    Note: The current implementation sends empty description to server,
    letting the server handle OpenAI API calls for consistency.
    
    Args:
        channel (int): GPIO pin number that triggered the callback
        
    Global Variables Modified:
        shutdownCounter: Reset to maximum value
    """
    global shutdownCounter
    print("button pressed")
    GPIO.output(config['gpio_pins']['led_1'],GPIO.HIGH)
    GPIO.output(config['gpio_pins']['led_2'],GPIO.LOW)
    shutdownCounter = config['shutdown_counter_max']
    captureImageOpenai()

def buttonCallback2(channel):
    """
    GPIO callback for shutdown button press (default GPIO 5).
    
    This function implements a multi-press graceful shutdown mechanism.
    Users must press the shutdown button multiple times (configured via
    shutdown_counter_max) to initiate system shutdown. This prevents
    accidental shutdowns while providing a reliable shutdown method.
    
    Behavior:
    1. Decrements shutdown counter on each press
    2. Updates LED indicators to show shutdown progress
    3. Executes system shutdown when counter reaches zero
    
    Args:
        channel (int): GPIO pin number that triggered the callback
        
    Global Variables Modified:
        shutdownCounter: Decremented on each press
        
    System Effects:
        Executes 'sudo shutdown now' when counter reaches zero
    """
    global shutdownCounter
    print("button 2 pressed")
    GPIO.output(config['gpio_pins']['led_2'],GPIO.HIGH)
    GPIO.output(config['gpio_pins']['led_1'],GPIO.HIGH)
    shutdownCounter = shutdownCounter - 1
    if shutdownCounter == 0:
        GPIO.output(config['gpio_pins']['led_2'],GPIO.HIGH)
        GPIO.output(config['gpio_pins']['led_1'],GPIO.HIGH)
        os.system("sudo shutdown now")

def buttonCallback3(channel):
    """
    GPIO callback for Google Gemini button press (default GPIO 26).
    
    This function is triggered when the Google Gemini button is pressed. It:
    1. Sets LED status indicators (different pattern from OpenAI)
    2. Resets shutdown counter
    3. Triggers image capture and Google Gemini processing
    
    Unlike the OpenAI callback, this function processes the image locally
    using Google's Gemini Pro Vision API and sends the description to the server.
    
    Args:
        channel (int): GPIO pin number that triggered the callback
        
    Global Variables Modified:
        shutdownCounter: Reset to maximum value
    """
    global shutdownCounter
    print("button 3 pressed")
    GPIO.output(config['gpio_pins']['led_1'],GPIO.LOW)
    GPIO.output(config['gpio_pins']['led_2'],GPIO.HIGH)
    shutdownCounter = config['shutdown_counter_max']
    captureImageGoogle()
    
def post_content(description, base64_image):
    """
    Post image and description to the Mnemosyne content server.
    
    This function sends a POST request to the configured content server
    with the processed image and description. The server endpoint expects
    a JSON payload with specific fields for storage in the database.
    
    Args:
        description (str): AI-generated description of the image
                          (can be empty string for server-side processing)
        base64_image (str): Base64-encoded JPEG image data
        
    JSON Payload:
        {
            "image": base64_image,
            "description": description,
            "deviceid": devId  # Device identifier (IP address)
        }
        
    Global Variables Used:
        devId: Device identifier for tracking image source
        config['contentserver_url']: Server endpoint URL
        
    Network Effects:
        HTTP POST request to content server
        Response logged to console for debugging
    """
    global picam2
    
    # Create the JSON payload
    payload = {
        'image': base64_image,
        'description': description,
        'deviceid' : devId
    }

    # Make the POST request
    response = requests.post(config['contentserver_url'], json=payload)

    # Print the response from the server
    print(response.text)

def analyze_image_google(img):
    """
    Analyze an image using Google Gemini Pro Vision API.
    
    This function sends a PIL Image object to Google's Gemini Pro Vision API
    for detailed scene analysis. It configures the API client and generates
    comprehensive descriptions including object detection, spatial relationships,
    and scene reasoning.
    
    Args:
        img (PIL.Image): PIL Image object to be analyzed
        
    Returns:
        str: Detailed description from Gemini Pro Vision
             Includes objects, locations, and scene reasoning
             
    Raises:
        google.api_core.exceptions.GoogleAPIError: If API call fails
        Exception: Various API-related exceptions
        
    Configuration Used:
        config['google_api_key']: Google AI Studio API key
        config['google_model']: Model name (typically 'gemini-pro-vision')
    """

    genai.configure(api_key=config['google_api_key'])

    model = genai.GenerativeModel(config['google_model'])
    response = model.generate_content(["What is in this image? Be as specific as possible, and list all attributes about the detected objects.  Provide relative locations of objects. Provide your best guesses on scene this is and your reasoning for these guesses.", img], stream=True)
    response.resolve()

    return response.text

def analyze_image(base64_image):
    """
    Analyze an image using OpenAI GPT-4 Vision API.
    
    This function sends a base64-encoded image to OpenAI's GPT-4 Vision API
    for scene analysis. It uses detailed prompts to get comprehensive
    descriptions including object detection, spatial relationships, and scene reasoning.
    
    Note: This function is currently unused in the main flow (captureImageOpenai
    sends empty descriptions to server), but is available for local processing.
    
    Args:
        base64_image (str): Base64-encoded JPEG image data
        
    Returns:
        dict: OpenAI API response containing the image analysis
              Expected structure: {'choices': [{'message': {'content': str}}]}
              
    Raises:
        requests.RequestException: If HTTP request to OpenAI API fails
        KeyError: If OpenAI API key is missing from config
        
    Configuration Used:
        config['openai_api_key']: OpenAI API key
        config['openai_model']: Model name (typically 'gpt-4o')
        config['max_tokens']: Maximum tokens in response
    """
    global picam2
        
    headers = { "Content-Type":
    "application/json", "Authorization": f"Bearer {config['openai_api_key']}" }

    payload = {
      "model": config['openai_model'],
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "What is in this image? Be as specific as possible, and list all attributes about the detected objects.  Provide relative locations of objects. Provide your best guesses on scene this is and your reasoning for these guesses."
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": config['max_tokens']
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())
    return response.json()

def capture_image_and_save_to_base64():
    """
    Capture an image using PiCamera2 and convert to base64 encoding.
    
    This function handles the complete camera operation cycle:
    1. Initialize PiCamera2 object if needed
    2. Detect device IP address on first run
    3. Configure camera for preview and still capture
    4. Capture image to numpy array
    5. Convert to PIL Image and save temporary file
    6. Encode image as base64 string for transmission
    
    Camera Operation:
    - Uses preview configuration for initial setup and auto-exposure
    - Switches to still configuration for high-quality capture
    - Properly starts/stops camera to avoid resource conflicts
    
    Returns:
        tuple: (base64_string, PIL_Image)
               base64_string (str): Base64-encoded JPEG data for transmission
               PIL_Image (PIL.Image): PIL Image object for local processing
               
    Global Variables Modified:
        picam2: PiCamera2 instance (created on first use)
        firstTime: Flag for first-time IP detection
        devId: Device identifier (set to IP address)
        ip: Device IP address
        
    File System Effects:
        Creates temporary image file at config['camera_temp_path']
        
    Raises:
        Exception: Various camera and image processing exceptions
    """
    global picam2
    global firstTime

    # Create a Picamera2 object
    if picam2 == None:
        picam2 = Picamera2()

    if firstTime == 0:
        print("Querying IP")
        getIP()
        firstTime = 1



    # Configure the camera with a preview configuration and start the camera
    preview_config = picam2.create_preview_configuration()
    # preview_config["transform"] = libcamera.Transform(hflip=1, vflip=0)
    picam2.configure(preview_config)
    picam2.start()

    # Wait a bit for the camera to adjust (e.g., auto-exposure)
    time.sleep(1)

    # Stop the camera before reconfiguring it for still capture
    picam2.stop()

    # Reconfigure the camera for still capture and start the camera again
    still_config = picam2.create_still_configuration()
    picam2.configure(still_config)
    picam2.start()

    # Capture an image to a numpy array
    capture = picam2.capture_array()

    # Stop the camera after capturing the image
    picam2.stop()
    
    # Convert the numpy array to a PIL Image
    img = Image.fromarray(capture)
    #img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # Save the image as a JPEG file in the current directory
    file_path = config['camera_temp_path']
    img.save(file_path)
    print(f"Image saved as {file_path}")

    # Prepare a bytes buffer to save the image for base64 encoding
    buffered = BytesIO()

    # Save the image to the buffer again for base64 encoding
    img.save(buffered, format="JPEG")

    # Convert the buffer content into a base64 string
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return img_str, img

#
# set up two switches and two LEDs
#
def initGpio():
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    GPIO.setup(config['gpio_pins']['openai_button'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config['gpio_pins']['shutdown_button'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config['gpio_pins']['google_button'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config['gpio_pins']['led_1'], GPIO.OUT)
    GPIO.setup(config['gpio_pins']['led_2'], GPIO.OUT)
    GPIO.add_event_detect(config['gpio_pins']['openai_button'],GPIO.RISING,callback=buttonCallback)
    GPIO.add_event_detect(config['gpio_pins']['shutdown_button'],GPIO.RISING,callback=buttonCallback2)
    GPIO.add_event_detect(config['gpio_pins']['google_button'],GPIO.RISING,callback=buttonCallback3)
    
#
# Capture an image, save it as a JPEG file, and get the base64 encoded string
# then call GPT4-Vision
#
# the pos_content() call posts the image and description to the content server
#
def captureImageOpenai():
    global picam2
        
    GPIO.output(config['gpio_pins']['led_2'],GPIO.HIGH)
    GPIO.output(config['gpio_pins']['led_1'],GPIO.HIGH)
    image_base64, saved_image = capture_image_and_save_to_base64()
    GPIO.output(config['gpio_pins']['led_2'],GPIO.LOW)

    #
    # this is where to comment out code to call LLM
    # and pass blank description to server and let
    # the call happen there
    #
    try:
        # result = analyze_image(image_base64)
        # description = result['choices'][0]['message']['content']
        description = ''
        post_content(description, image_base64)
        # print(description)
    except:
        picam2 = None
        
    GPIO.output(config['gpio_pins']['led_1'],GPIO.LOW)

#
# Capture an image, save it as a JPEG file, and get the base64 encoded string
# then call Gemini Pro
#
def captureImageGoogle():
    global picam2
        
    GPIO.output(config['gpio_pins']['led_2'],GPIO.HIGH)
    GPIO.output(config['gpio_pins']['led_1'],GPIO.HIGH)
    image_base64, saved_image = capture_image_and_save_to_base64()
    GPIO.output(config['gpio_pins']['led_1'],GPIO.LOW)

    try:
        result = analyze_image_google(saved_image)
        description = result
        post_content(description, image_base64)
        print(description)
    except:
        picam2 = None
        
    GPIO.output(config['gpio_pins']['led_2'],GPIO.LOW)

def getIP():
    """
    Detect the device's IP address for identification purposes.
    
    This function queries the system routing table to find the IP address
    associated with the wireless interface (wlan0). The detected IP address
    is used as the device identifier when sending data to the server.
    
    Process:
    1. Execute 'ip -j -4 route' command to get routing information
    2. Parse JSON output to find wlan0 interface routes
    3. Extract the preferred source IP address (prefsrc)
    4. Set global variables for device identification
    
    Global Variables Modified:
        ip (str): Device IP address from wlan0 interface
        devId (str): Device identifier (set to same as ip)
        
    System Command Used:
        'ip -j -4 route': Linux command to get IPv4 routing table in JSON format
        
    Note:
        This function assumes a wireless connection (wlan0). For Ethernet
        connections, the interface name would be different (e.g., eth0).
    """
    global ip
    global devId

    # Query system routing table for network interface information
    routes = json.loads(os.popen("ip -j -4 route").read())
    print("Routes:", routes)

    # Find the wireless interface (wlan0) and extract IP address
    for r in routes:
        if r.get("dev") == "wlan0" and r.get("prefsrc"):
            ip = r['prefsrc']
            continue
    devId = ip  # Use IP address as device identifier
    print(f"Device ID set to: {devId}")


    
# Main execution: Initialize GPIO and enter monitoring loop
if __name__ == "__main__":
    """
    Main execution block for the Mnemosyne camera device.
    
    This block:
    1. Initializes GPIO pins for buttons and LEDs
    2. Sets initial LED state (both on for ready status)
    3. Enters infinite monitoring loop
    4. Handles cleanup on exit (though normally unreachable)
    
    The infinite loop keeps the program running to handle GPIO events.
    Button presses are handled asynchronously via GPIO callbacks.
    """
    try:
        print("Initializing Mnemosyne Camera Device...")
        initGpio()  # Set up GPIO pins and event detection
        
        # Set initial LED state to indicate device is ready
        GPIO.output(config['gpio_pins']['led_2'], GPIO.HIGH)
        GPIO.output(config['gpio_pins']['led_1'], GPIO.HIGH)
        print("Device ready - LEDs on, waiting for button presses...")
        
        # Main monitoring loop - keeps program alive for GPIO events
        while True:
            time.sleep(1)  # Minimal CPU usage while waiting for events
            
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        GPIO.cleanup()  # Clean up GPIO resources on exit
        print("GPIO cleanup completed")
    

