import os
import threading
import json
import time
from flask import Flask, render_template, request, Response, stream_with_context, send_from_directory, jsonify
from flask_cors import CORS
import yt_dlp
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"], "expose_headers": ["Content-Disposition"]}})

# Global variables
video_info = None
download_path = os.path.join(os.path.expanduser("~"), "Downloads")
current_filename = None

# Function to clean YouTube URL
def clean_url(url):
    base_url = url.split('?')[0]
    if 'youtu.be' in base_url:
        video_id = base_url.split('/')[-1]
        if not video_id:
            raise ValueError("Invalid youtu.be URL: No video ID found")
        return f"https://www.youtube.com/watch?v={video_id}"
    elif 'youtube.com/watch' in base_url:
        query_params = url.split('?')[-1] if '?' in url else ''
        params = dict(param.split('=') for param in query_params.split('&') if '=' in param)
        video_id = params.get('v')
        if not video_id:
            raise ValueError("Invalid YouTube URL: No video ID found in query parameters")
        return f"https://www.youtube.com/watch?v={video_id}"
    else:
        raise ValueError("Unsupported URL format: Must be a youtu.be or youtube.com/watch URL")

# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to load video details
@app.route('/load', methods=['POST'])
def load():
    global video_info
    data = request.get_json(force=True)
    url = data.get('url')
    if not url:
        return jsonify({'error': 'Please enter a YouTube URL'}), 400

    try:
        clean_url_val = clean_url(url)
        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'socket_timeout': 30,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url_val, download=False)
            if not info:
                raise ValueError("No video info returned by yt-dlp")
            video_info = info

        formats = info.get('formats', [])
        resolutions = []
        for fmt in formats:
            height = fmt.get('height')
            if height:
                resolution = f"{height}p"
                if resolution not in resolutions:
                    resolutions.append(resolution)

        resolutions.sort(key=lambda x: int(x[:-1]), reverse=True)
        response_data = {
            'title': info.get('title', 'Unknown Title'),
            'thumbnail': info.get('thumbnail', ''),
            'resolutions': resolutions
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': f'Failed to load video: {str(e)}'}), 500

# Progress hook for yt-dlp
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').replace('%', '')
        try:
            percent_float = float(percent)
            yield json.dumps({'progress': percent_float}) + '\n'
        except ValueError:
            pass
    elif d['status'] == 'finished':
        yield json.dumps({'status': 'Download completed', 'filename': current_filename}) + '\n'

# Generator for download progress
def download_generator(video_info, format_type, resolution):
    global current_filename
    video_title = "".join(c for c in video_info.get('title', 'video') if c.isalnum() or c in (' ', '_', '-')).rstrip()
    # Remove additional invalid characters for Windows
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        video_title = video_title.replace(char, '')
    current_filename = f"{video_title}_{int(time.time())}.{format_type.lower()}"
    save_path = os.path.join(download_path, current_filename)
    
    os.makedirs(download_path, exist_ok=True)
    app.logger.info(f"Saving file to: {save_path}")

    try:
        ydl_opts = {
            'outtmpl': save_path,
            'progress_hooks': [progress_hook],
        }
        if format_type == "MP4":
            ydl_opts['format'] = f'bestvideo[height<={resolution[:-1]}]+bestaudio/best[height<={resolution[:-1]}]'
            ydl_opts['merge_output_format'] = 'mp4'
        else:
            ydl_opts['format'] = 'bestaudio'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            def download_task():
                ydl.download([video_info['webpage_url']])

            thread = threading.Thread(target=download_task)
            thread.start()

            progress_generator = progress_hook({'status': 'downloading'})
            while thread.is_alive():
                try:
                    update = next(progress_generator)
                    yield update
                except StopIteration:
                    break
                time.sleep(0.1)

            thread.join()
            time.sleep(1)  # Ensure the file is fully written
            if os.path.exists(save_path):
                yield json.dumps({'status': 'Download completed', 'filename': current_filename}) + '\n'
            else:
                yield json.dumps({'error': 'File was not created on the server'}) + '\n'
    except Exception as e:
        yield json.dumps({'error': f'Download failed: {str(e)}'}) + '\n'

# Route to handle download
@app.route('/download', methods=['POST'])
def download():
    global video_info
    if not video_info:
        return Response(json.dumps({'error': 'Please load a video first'}) + '\n', content_type='text/event-stream')

    data = request.get_json(force=True)
    format_type = data.get('format')
    resolution = data.get('resolution')
    if not resolution and format_type == 'MP4':
        return Response(json.dumps({'error': 'Please select a resolution'}) + '\n', content_type='text/event-stream')

    return Response(stream_with_context(download_generator(video_info, format_type, resolution)), content_type='text/event-stream')

# Route to serve downloaded files
@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        # Log the request details
        app.logger.info(f"Attempting to serve file: {filename}")
        app.logger.info(f"Download path: {download_path}")
        full_path = os.path.join(download_path, filename)
        app.logger.info(f"Full file path: {full_path}")
        
        # Check if the file exists
        if not os.path.exists(full_path):
            app.logger.error(f"File does not exist: {full_path}")
            return jsonify({'error': f'File not found: {filename}'}), 404

        # Serve the file
        response = send_from_directory(download_path, filename, as_attachment=True)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Log successful serving
        app.logger.info(f"File served successfully: {filename}")
        
        # Delete the file after serving
        try:
            time.sleep(0.5)  # Ensure the file is fully sent
            os.remove(full_path)
            app.logger.info(f"File deleted successfully: {filename}")
        except Exception as delete_error:
            app.logger.error(f"Failed to delete file {filename}: {str(delete_error)}")
        
        return response
    except Exception as e:
        app.logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': f'Error serving file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)