import os
import threading
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import yt_dlp

# Initialize the main window
root = Tk()
root.title("YouTube Downloader")
root.geometry("600x400")
root.resizable(False, False)

# Global variable to store video info
video_info = None

# Create and pack the URL entry field
url_label = Label(root, text="Enter YouTube URL:", font="Arial 12 bold")
url_label.pack(pady=10)
url_entry = Entry(root, width=50, font="Arial 10")
url_entry.pack(pady=5)

# Create and pack the "Load Video" button
load_button = Button(root, text="Load Video", font="Arial 12", command=lambda: load_video())
load_button.pack(pady=10)

# Create and pack the resolution selection Combobox
resolution_label = Label(root, text="Select Resolution:", font="Arial 12 bold")
resolution_label.pack(pady=10)
resolution_var = StringVar()
resolution_combobox = ttk.Combobox(root, textvariable=resolution_var, state="readonly", width=20)
resolution_combobox.pack(pady=5)

# Create and pack the "Download" button, initially disabled
download_button = Button(root, text="Download", font="Arial 12", command=lambda: download_video(), state=DISABLED)
download_button.pack(pady=10)

# Function to load video details using yt-dlp
def load_video():
    global video_info
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    try:
        # Clean the URL by removing query parameters after the video ID
        base_url = url.split('?')[0]
        if 'youtu.be' in base_url:
            video_id = base_url.split('/')[-1]
            if not video_id:
                raise ValueError("Invalid youtu.be URL: No video ID found")
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
        elif 'youtube.com/watch' in base_url:
            query_params = url.split('?')[-1] if '?' in url else ''
            params = dict(param.split('=') for param in query_params.split('&') if '=' in param)
            video_id = params.get('v')
            if not video_id:
                raise ValueError("Invalid YouTube URL: No video ID found in query parameters")
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
        else:
            raise ValueError("Unsupported URL format: Must be a youtu.be or youtube.com/watch URL")

        print(f"Attempting to load video with URL: {clean_url}")
        load_button.config(state=DISABLED)

        # Use yt-dlp to fetch video info
        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo',  # Fetch video streams
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            video_info = info

        # Extract available resolutions
        formats = info.get('formats', [])
        resolutions = []
        for fmt in formats:
            height = fmt.get('height')
            if height:
                resolution = f"{height}p"
                if resolution not in resolutions:
                    resolutions.append(resolution)

        # Sort resolutions in descending order
        resolutions.sort(key=lambda x: int(x[:-1]), reverse=True)
        resolution_combobox['values'] = resolutions
        if resolutions:
            resolution_var.set(resolutions[0])
            download_button.config(state=NORMAL)
        else:
            messagebox.showerror("Error", "No video streams available")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load video: {str(e)}")
    finally:
        load_button.config(state=NORMAL)

# Function to perform the download in a separate thread
def perform_download(resolution, save_path):
    try:
        # Configure yt-dlp options for downloading
        ydl_opts = {
            'format': f'bestvideo[height<={resolution[:-1]}]+bestaudio/best[height<={resolution[:-1]}]',  # Select video and audio
            'outtmpl': save_path,  # Output path
            'merge_output_format': 'mp4',  # Merge into mp4
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_info['webpage_url']])
        root.after(0, lambda: messagebox.showinfo("Success", "Download completed"))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
    finally:
        root.after(0, lambda: download_button.config(text="Download", state=NORMAL))

# Function to handle the download process
def download_video():
    global video_info
    if video_info is None:
        messagebox.showerror("Error", "Please load a video first")
        return
    resolution = resolution_var.get()
    if not resolution:
        messagebox.showerror("Error", "Please select a resolution")
        return
    save_path = filedialog.asksaveasfilename(
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4")],
        initialfile=video_info.get('title', 'video')
    )
    if save_path:
        download_button.config(text="Downloading...", state=DISABLED)
        threading.Thread(target=perform_download, args=(resolution, save_path), daemon=True).start()

# Start the main loop
root.mainloop()