# app.py - Your Python Backend Server Code (Updated for title and thumbnail)
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import logging

app = Flask(__name__)

# Suppress yt-dlp warnings if desired, though seeing them can be helpful for debugging
logging.getLogger('yt_dlp').setLevel(logging.ERROR)

# ADDED: A new route to confirm the server is running correctly.
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

    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'simulate': True,  # Only extract info, don't actually download
        'force_generic_extractor': False,
        'skip_download': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)

            direct_url = info_dict.get('url')  # Get the direct URL
            title = info_dict.get('title', 'Downloaded Video')  # Get the title, default if not found
            thumbnail_url = info_dict.get('thumbnail') # Get the thumbnail URL

            if direct_url:
                # Return the direct URL, title, and thumbnail URL
                return jsonify({
                    "direct_url": direct_url,
                    "title": title,
                    "thumbnail": thumbnail_url
                })
            else:
                app.logger.error(f"Could not extract direct URL for: {video_url}. Info dict keys: {info_dict.keys()}")
                return jsonify({"error": "Could not extract direct download URL from video info."}), 500

    except Exception as e:
        app.logger.error(f"Error processing URL {video_url}: {e}", exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
