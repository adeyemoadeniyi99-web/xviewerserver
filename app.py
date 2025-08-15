# app.py - Backend server for extracting video info via yt-dlp
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from flask_cors import CORS
import logging
import os

app = Flask(__name__)
CORS(app)

# Set the logging level for yt-dlp to suppress verbose output
logging.getLogger('yt_dlp').setLevel(logging.ERROR)

@app.route('/', methods=['GET'])
def hello_world():
    """
    A simple route to confirm the backend server is running.
    """
    return "Backend server is running!"

@app.route('/get-youtube-url', methods=['POST'])
def get_youtube_url():
    """
    Extracts video information and a direct download URL from a given URL
    using the yt-dlp library.
    """
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No JSON data provided"}), 400

    video_url = data.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Received request for URL: {video_url}")

    # Define the yt-dlp options, including format selection and a user agent
    ydl_opts = {
        # This format string is more robust for YouTube, ensuring a high-quality
        # video and audio stream are selected and merged.
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'noplaylist': True,
        'quiet': True,
        'skip_download': True,
        # Using a valid user-agent helps bypass some anti-bot detection
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    
    # Check for a cookies file if one exists
    if os.path.isfile('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    # --- NEW: PROXY IMPLEMENTATION ---
    # Retrieve the proxy URL from environment variables.
    # This allows you to set it on Render.com without changing the code.
    proxy_url = os.environ.get('PROXY_URL')
    if proxy_url:
        # If a proxy is found, add it to the yt-dlp options.
        # This is the key fix for getting around YouTube's IP blocking.
        print(f"Using proxy from environment: {proxy_url}")
        ydl_opts['proxy'] = proxy_url
    else:
        print("No PROXY_URL environment variable found. Continuing without a proxy.")
    
    try:
        # Use a `with` statement for safe resource management
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            
            # Use .get() with a default value to prevent errors if a key is missing
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
        # Catch specific yt-dlp download errors for better debugging
        print(f"DownloadError: {str(e)}")
        return jsonify({
            "error": "Download failed — video may be blocked or unavailable.",
            "details": str(e)
        }), 400
    except Exception as e:
        # Catch all other unexpected errors
        app.logger.error(f"Error processing URL {video_url}: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Get the port from the environment, defaulting to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
