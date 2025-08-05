# app.py - Your Python Backend Server Code (Updated for yt-dlp compatibility)
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app) # Re-added: Enable CORS for all routes

# Suppress yt-dlp warnings to reduce log noise
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

    # Print the URL to logs for debugging
    print(f"Received request for URL: {video_url}")

    # The yt-dlp options. 'simulate' is redundant with 'skip_download'.
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'skip_download': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # The extract_info method is what yt-dlp uses to get the metadata
            # without downloading the video.
            info_dict = ydl.extract_info(video_url, download=False)
            
            # Extract the direct URL, title, and thumbnail from the info dictionary
            direct_url = info_dict.get('url')
            title = info_dict.get('title', 'Downloaded Video')
            thumbnail_url = info_dict.get('thumbnail')

            if direct_url and title:
                # Success! Return the data as JSON
                return jsonify({
                    "direct_url": direct_url,
                    "title": title,
                    "thumbnail": thumbnail_url
                })
            else:
                # If we couldn't find a direct URL or title, something went wrong
                return jsonify({"error": "Could not extract direct download URL or title."}), 500

    except Exception as e:
        # Catch any errors from yt-dlp and return a user-friendly message
        app.logger.error(f"Error processing URL {video_url}: {e}", exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
