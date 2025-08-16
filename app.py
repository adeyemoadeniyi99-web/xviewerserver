@app.route('/download', methods=['POST'])
def download():
    """
    Extract video info + available direct download links from YouTube using yt-dlp.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    video_url = data.get('url')
    if not video_url:
        return jsonify({"error": "No 'url' field provided"}), 400

    print(f"Received request for URL: {video_url}")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'noplaylist': True,
        'quiet': True,
        'skip_download': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }

    # Use cookies if present
    if os.path.isfile('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    # Add proxy if set in environment
    proxy_url = os.environ.get('PROXY_URL')
    if proxy_url:
        print(f"Using proxy: {proxy_url}")
        ydl_opts['proxy'] = proxy_url

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)

            # Extract available formats (video/audio)
            formats = []
            for f in info_dict.get('formats', []):
                # Only include formats with a playable URL
                if f.get('url'):
                    formats.append({
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "resolution": f.get("resolution") or f"{f.get('height', '?')}p",
                        "filesize": f.get("filesize"),
                        "url": f.get("url"),
                    })

            return jsonify({
                "title": info_dict.get('title', 'Unknown'),
                "thumbnail": info_dict.get('thumbnail'),
                "formats": formats  # <-- returns multiple download URLs
            })

    except DownloadError as e:
        return jsonify({
            "error": "Download failed — video may be blocked or unavailable.",
            "details": str(e)
        }), 400
    except Exception as e:
        app.logger.error(f"Error processing {video_url}: {e}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
