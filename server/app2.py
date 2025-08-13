#!/usr/bin/env python3
"""
Mnemosyne Server - Visual Memory Management System

This Flask web application serves as the central server for the Mnemosyne visual memory system.
It receives base64-encoded images from IoT camera devices, processes them using OpenAI's GPT-4
Vision API, stores the results in a SQLite database, and provides web interfaces for content
management and natural language querying of stored scenes.

Main Features:
- RESTful API endpoint for receiving images from camera devices
- AI-powered scene analysis using OpenAI GPT-4 Vision
- SQLite database storage for images, descriptions, and metadata
- Web interface for content management (view, delete, filter)
- Natural language querying of stored scenes with date/time filtering
- Bootstrap-styled responsive web interface

API Endpoints:
- POST /add_content: Receives images from camera devices
- GET /get_contents: Returns JSON of all stored content
- GET/POST /contents: Web interface for content management
- GET/POST /query: Natural language query interface

Author: Mnemosyne Project
License: See project documentation
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
from openai import OpenAI
import openai
import requests
import sqlite3
import json
import os
import sys

def load_config():
    """
    Load configuration from config.json file.
    
    This function loads the application configuration including API keys,
    database settings, Flask configuration, and AI model parameters.
    
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

# Load configuration and initialize Flask application
config = load_config()
app = Flask(__name__)

def ask_gpt4(question, entries_text):
    """
    Query OpenAI GPT-4 with a question about stored scene descriptions.
    
    This function takes a user question and a formatted string of scene entries
    (timestamp + description pairs) and uses OpenAI's Chat Completions API to
    generate an intelligent response based on the stored visual memory data.
    
    Args:
        question (str): The user's natural language question
        entries_text (str): Formatted string of scene entries with timestamps
                           Format: "YYYY-MM-DD HH:MM:SS: description\n..."
    
    Returns:
        str: GPT-4's response to the question based on the scene data
        
    Raises:
        openai.OpenAIError: If API call fails
        KeyError: If response structure is unexpected
    """
    client = OpenAI()
    

    completion = client.chat.completions.create(
      model=config['openai_model'],
      messages=[
            {"role": "system", "content": "You are provided a set of timestamps followed by descriptions of what was observed at that time. Please infer the answer to the question based on the descriptions provided."},
            {"role": "user", "content": question},
            {"role": "user", "content": entries_text}

      ]
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def analyze_image(base64_image):
    """
    Analyze an image using OpenAI GPT-4 Vision API.
    
    This function takes a base64-encoded image and sends it to OpenAI's
    GPT-4 Vision API for scene analysis. The API returns a description
    of objects, scene type, and other visual elements detected in the image.
    
    Args:
        base64_image (str): Base64-encoded JPEG image data
        
    Returns:
        dict: OpenAI API response containing the image analysis
              Expected structure: {'choices': [{'message': {'content': str}}]}
              
    Raises:
        requests.RequestException: If HTTP request to OpenAI API fails
        KeyError: If OpenAI API key is missing from config
    """
        
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
              "text": "What is in this image? List all detected objects.  Provide your best guesses on what scene this is. Be concise in your answer and drop unnecessary words like the or and in your response. Strive to minimize word count in your answer"
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


#
# connect to local database for entries
#
def get_db_connection():
    conn = sqlite3.connect(config['database_path'])
    conn.row_factory = sqlite3.Row
    return conn

#
# create new database if it doesnt already exist
#
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY, 
            image TEXT, 
            description TEXT, 
            timestamp TEXT,
            deviceid TEXT
        )
    ''')
    conn.commit()
    conn.close()

#
# home page with some choices
#
@app.route('/')
def home():
    return '''
        <h1>Content Management</h1>
        <ul>
            <li><a href="/add_content">Add Content</a></li>
            <li><a href="/get_contents">View All Contents</a></li>
            <li><a href="/contents">Manage Contents</a></li>
            <li><a href="/contents?i=1">Manage Contents (with images)</a></li>
            <li><a href="/query">Ask Question</a></li>
        </ul>
    '''

#
# this route supports only POST. It takes a JSON parameter,
#   and current timestamp will be added
#
#   The top level JSON fields are:
#   image - base64 encoded image
#   description - string containing description of room
#   deviceid - string representing device
#   
@app.route('/add_content', methods=['POST'])
def add_content():
    content_data = request.json
    image = content_data['image']

    #
    # two paths here - either we use the description that is passed in,
    # or we ask GPT to generate result
    #
    # comment out one or the other
    #
    #
    # description = content_data['description']

    temp = analyze_image(image)
    try:
        description = temp['choices'][0]['message']['content']
    except:
        print("Unable to get description")
        return jsonify({'message': 'No Content added'}), 201
    
    deviceid = content_data.get('deviceid', 'Unknown')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    conn.execute('INSERT INTO content (image, description, timestamp, deviceid) VALUES (?, ?, ?, ?)',
                 (image, description, timestamp, deviceid))
    conn.commit()
    conn.close()

    print(description)
    return jsonify({'message': 'Content added successfully'}), 201

#
#   this route returns a JSON representation of all entries
#   output can be long
#
@app.route('/get_contents', methods=['GET'])
def get_contents():
    conn = get_db_connection()
    contents = conn.execute('SELECT * FROM content').fetchall()
    conn.close()

    content_list = []
    for content in contents:
        content_list.append({'id': content['id'], 'image': content['image'], 
                             'description': content['description'], 
                             'timestamp': content['timestamp'],
                             'deviceid': content['deviceid']})

    return jsonify(content_list)

#
#   this route returns content
#   GET - return a page with all entries in a table
#           if parameter i is set to 1, then images will be included
#   POST - delete selected entries
#
@app.route('/contents', methods=['GET', 'POST'])
def manage_contents():

    start_date = None
    
    conn = get_db_connection()
    if request.method == 'POST':

        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']

        print(start_date)



        
        selected_ids = request.form.getlist('content_id')
        for content_id in selected_ids:
            conn.execute('DELETE FROM content WHERE id = ?', (content_id,))
        conn.commit()

    if start_date is None:
        contents = conn.execute('SELECT * FROM content').fetchall()
    else:
        # Combine date and time into full datetime strings
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"

        query = "SELECT * FROM content WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp"
        print(query)
        contents = conn.execute(query, (start_datetime, end_datetime)).fetchall()
        
    conn.close()

    include_images = request.args.get('i', '0') == '1'

    # Note: Direct templating syntax is used here without f-string for dynamic HTML generation
    html_template = '''
        <html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <title>{% block title %}My Flask App{% endblock %}</title>
</head>
            <body>
                <h2>Manage Contents</h2>
                    <main class="container mt-4">
                <form method="post">
                    <table>
                        <tr>
                            <th>Select</th>
                            <th>Timestamp</th>
                            <th>Description</th>
                            <th>DeviceID</th>
                            ''' + ('<th>Image</th>' if include_images else '') + '''
                        </tr>
                        {% for content in contents %}
                        <tr>
                            <td><input type="checkbox" name="content_id" value="{{ content["id"] }}"></td>
                            <td>{{ content["timestamp"] }}</td>
                            <td>{{ content["description"] }}</td>
                            <td>{{ content["deviceid"] }}</td>
                            ''' + ('<td><img src="data:image/jpeg;base64,{{ content["image"] }}"></td>' if include_images else '') + '''
                        </tr>
                        {% endfor %}
                    </table>
                    <input type="submit" value="Delete" style="margin-top: 10px;"><br />
            Start Date: <input type="date" name="start_date">
            Start Time: <input type="time" name="start_time"><br>
            End Date: <input type="date" name="end_date">
            End Time: <input type="time" name="end_time"><br>
            <input type="submit" value="Submit">
                </form>
                </main>
            </body>
        </html>
    '''

    return render_template_string(html_template, contents=contents)

#
#   ask questions about the scenes between two time periods.  parameters are:
#
#   question
#   start_time
#   start_date
#   end_date
#   end_time
#
#   GET - show the page
#   POST - process request
#
@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        question = request.form['question']
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']

        # Combine date and time into full datetime strings
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"

        conn = get_db_connection()
        query = "SELECT timestamp, description FROM content WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp"
        entries = conn.execute(query, (start_datetime, end_datetime)).fetchall()
        conn.close()

        # Prepend the question to the formatted entries text
        entries_text = "\n".join([f"{entry['timestamp']}: {entry['description']}" for entry in entries])
        print(entries_text)

        # Here you would make the call to the OpenAI API using entries_text
        response_text = ask_gpt4(question, entries_text)

        # Show the response along with the form for new queries
        return render_template_string(QUERY_PAGE_TEMPLATE, question=question, response=response_text, entries=entries_text)
    else:
        # Initial page load without any POST data
        return render_template_string(QUERY_PAGE_TEMPLATE, question="", response="", entries="")

# The QUERY_PAGE_TEMPLATE remains the same as previously defined
QUERY_PAGE_TEMPLATE = '''
<html>
    <head>
        <title>Query</title>
    </head>
    <body>
        <h1>Query Interface</h1>
        <form method="post">
            Question:<br>
            <textarea name="question" rows="4" cols="50">{{ question }}</textarea><br>
            Start Date: <input type="date" name="start_date">
            Start Time: <input type="time" name="start_time"><br>
            End Date: <input type="date" name="end_date">
            End Time: <input type="time" name="end_time"><br>
            <input type="submit" value="Submit">
        </form>
        <h2>Response:</h2>
        <p>{{ response }}</p>
        <h2>Database Entries:</h2>
        <p>{{ entries }}</p>
    </body>
</html>
'''

#
# simply start the server
#
if __name__ == '__main__':
    init_db()  # Ensure the database and table are created
    app.run(debug=config['flask_debug'], host=config['flask_host'], port=config['flask_port'])

