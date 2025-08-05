# app.py - Backend server for extracting video info via yt-dlp
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from flask_cors import CORS
import logging
import os

app = Flask(__name__)
CORS(app)
logging.getLogger('yt_dlp').setLevel(logging.ERROR)

@app.route('/', methods=['GET'])
def hello_world():
    return "Backend server is running!"

@app.route('/get-youtube-url', methods=['POST'])
def get_youtube_url():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No JSON data provided"}), 400

    video_url = data.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Received request for URL: {video_url}")

    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'skip_download': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    if os.path.isfile('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            direct_url = info_dict.get('url')
            title = info_dict.get('title', 'Downloaded Video')
            thumbnail_url = info_dict.get('thumbnail')

            if direct_url and title:
                return jsonify({
                    "direct_url": direct_url,
                    "title": title,
                    "thumbnail": thumbnail_url
                })
            else:
                return jsonify({"error": "Could not extract direct download URL or title."}), 500

    except DownloadError as e:
        return jsonify({
            "error": "Download failed — video may be blocked or unavailable.",
            "details": str(e)
        }), 400
    except Exception as e:
        app.logger.error(f"Error processing URL {video_url}: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
