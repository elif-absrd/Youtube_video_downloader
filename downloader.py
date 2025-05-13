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
root.configure(bg="#1E1E1E")  # Dark background

# Apply custom styling
style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", fieldbackground="#2E2E2E", background="#2E2E2E", foreground="#FFFFFF", selectbackground="#3E3E3E", selectforeground="#FFFFFF")
style.configure("TButton", background="#3E3E3E", foreground="#FFFFFF", font=("Arial", 10))
style.map("TButton", background=[('active', '#4E4E4E')])

# Global variable to store video info
video_info = None

# Create main frame
main_frame = Frame(root, bg="#1E1E1E")
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# URL input and Load button row
url_frame = Frame(main_frame, bg="#1E1E1E")
url_frame.pack(fill="x", pady=10)

url_label = Label(url_frame, text="YouTube URL:", font=("Arial", 12, "bold"), fg="#FFFFFF", bg="#1E1E1E")
url_label.pack(side=LEFT, padx=(0, 10))

url_entry = Entry(url_frame, width=40, font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF", insertbackground="#FFFFFF", borderwidth=1, relief="solid")
url_entry.pack(side=LEFT, padx=(0, 10), ipady=5)

load_button = Button(url_frame, text="Load Video", font=("Arial", 10, "bold"), bg="#3E3E3E", fg="#FFFFFF", activebackground="#4E4E4E", relief="flat", command=lambda: load_video())
load_button.pack(side=LEFT)

# Resolution selection
resolution_frame = Frame(main_frame, bg="#1E1E1E")
resolution_frame.pack(pady=20)

resolution_label = Label(resolution_frame, text="Select Resolution:", font=("Arial", 12, "bold"), fg="#FFFFFF", bg="#1E1E1E")
resolution_label.pack()

resolution_var = StringVar()
resolution_combobox = ttk.Combobox(resolution_frame, textvariable=resolution_var, state="readonly", width=15, font=("Arial", 10))
resolution_combobox.pack(pady=10)

# Download button
download_button = Button(main_frame, text="Download", font=("Arial", 12, "bold"), bg="#3E3E3E", fg="#FFFFFF", activebackground="#4E4E4E", relief="flat", command=lambda: download_video(), state=DISABLED, width=15)
download_button.pack(pady=20)

# Status label
status_label = Label(main_frame, text="", font=("Arial", 10), fg="#BBBBBB", bg="#1E1E1E")
status_label.pack(pady=10)

# Function to load video details using yt-dlp
def load_video():
    global video_info
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    try:
        status_label.config(text="Loading video details...")
        load_button.config(state=DISABLED)
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
            status_label.config(text="Video loaded successfully")
        else:
            messagebox.showerror("Error", "No video streams available")
            status_label.config(text="")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load video: {str(e)}")
        status_label.config(text="")
    finally:
        load_button.config(state=NORMAL)

# Function to perform the download in a separate thread
def perform_download(resolution, save_path):
    try:
        status_label.config(text=f"Downloading {resolution} video...")
        # Configure yt-dlp options for downloading
        ydl_opts = {
            'format': f'bestvideo[height<={resolution[:-1]}]+bestaudio/best[height<={resolution[:-1]}]',  # Select video and audio
            'outtmpl': save_path,  # Output path
            'merge_output_format': 'mp4',  # Merge into mp4
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_info['webpage_url']])
        root.after(0, lambda: messagebox.showinfo("Success", "Download completed"))
        root.after(0, lambda: status_label.config(text="Download completed"))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
        root.after(0, lambda: status_label.config(text=""))
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