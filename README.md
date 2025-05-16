# YouTube Downloader GUI

A simple Python application to download YouTube videos with a graphical user interface (GUI) using `yt-dlp` and `tkinter`. Users can input a YouTube URL, select from available video resolutions, and save the video to their desired location.

## Features
- Input a YouTube video URL.
- Load available video resolutions.
- Select a resolution and download the video with audio.
- User-friendly error messages for invalid URLs or download issues.
- Responsive GUI with download progress handled in a separate thread.

## Requirements
- Python 3.6 or higher
- `yt-dlp` library (see `requirements.txt`)
- `tkinter` (included with standard Python installations)

## Installation
1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/elif-absrd/Youtube_video_downloader.git
   ```
   Alternatively, you can download the repository as a ZIP file and extract it.
2. Ensure Python 3.6+ is installed. Verify with:
   ```bash
   python --version
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```bash
   python downloader.py
   ```
2. Enter a valid YouTube video URL
3. Click **Load Video** to fetch available resolutions.
4. Select a resolution from the dropdown menu.
5. Click **Download**, choose a save location, and wait for the download to complete.
6. Success or error messages will appear upon completion.

## Screenshot
Here’s a preview of the YouTube Downloader GUI:

![YouTube Downloader GUI Screenshot](https://github.com/elif-absrd/Youtube_video_downloader/raw/main/screenshot.png)



## Limitations
- **Performance**: Large videos may take time to download. No progress bar is included in this version.
- **Dependency on yt-dlp**: Ensure `yt-dlp` is kept up to date to handle YouTube API changes.

## Legal Considerations
- **YouTube Terms of Service**: Downloading videos may violate YouTube's terms unless you have permission or the video is explicitly downloadable. Use this tool responsibly and only for content you have the right to download.
- **Copyright**: Ensure you have permission to download and use the content to avoid legal issues.

## Troubleshooting
- **Invalid URL Error**: Ensure the URL is correct and accessible.
- **No Resolutions Available**: The video may not have downloadable streams, or `yt-dlp` may need updating.
- **Download Fails**: Check your internet connection or try a different resolution.
- **Update**: If errors occur, update requirments:
  ```bash
  pip install --upgrade flask flask-cors yt-dlp
  ```