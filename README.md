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
   This installs `yt-dlp>=2024.5.10`.

## Usage
1. Run the application:
   ```bash
   python downloader.py
   ```
2. Enter a valid YouTube video URL (e.g., `https://www.youtube.com/watch?v=2lAe1cqCOXo`).
3. Click **Load Video** to fetch available resolutions.
4. Select a resolution from the dropdown menu.
5. Click **Download**, choose a save location, and wait for the download to complete.
6. Success or error messages will appear upon completion.

## Example
- URL: `https://www.youtube.com/watch?v=2lAe1cqCOXo`
- Resolutions available: 1080p, 720p, 480p, etc.
- Save as: `video_title.mp4`

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
- **Update yt-dlp**: If errors occur, update `yt-dlp`:
  ```bash
  pip install --upgrade yt-dlp
  ```

## Contributing
Feel free to fork this repository and submit pull requests for improvements, such as adding a progress bar or additional format options.

## Acknowledgments
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube video downloading.
- [tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework.
