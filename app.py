# app.py - Backend server for extracting video info via Replit yt-dlp worker
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import os

app = Flask(__name__)
CORS(app)

# Suppress verbose logging
logging.getLogger('yt_dlp').setLevel(logging.ERROR)

@app.route('/', methods=['GET'])
def hello_world():
    """
    Root route to confirm server is alive.
    """
    return jsonify({"message": "Backend server is running!"})

@app.route('/download', methods=['POST'])
def download():
    """
    Proxy YouTube info request to Replit worker.
    Accepts JSON body: { "url": "YOUTUBE_LINK" }
    Returns video info: direct URL, title, thumbnail
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    video_url = data.get('url')
    if not video_url:
        return jsonify({"error": "No 'url' field provided"}), 400

    print(f"Proxying request for URL: {video_url}")

    # Replit worker URL (replace with your actual Replit worker URL)
    WORKER_URL = "https://a660a3d7-037d-4ea6-91a9-272457186f2b-00-222micxxy3mrb.worf.replit.dev/"

    try:
        response = requests.get(WORKER_URL, params={"url": video_url}, timeout=20)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Worker request failed: {e}", exc_info=True)
        return jsonify({"error": "Worker request failed", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
