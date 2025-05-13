import os
import threading
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import yt_dlp
from PIL import Image, ImageTk
import urllib.request
import io

# Initialize the main window
root = Tk()
root.title("YouTube Downloader")
root.geometry("700x500")
root.resizable(False, False)
root.configure(bg="#1E1E1E")  # Dark background

# Apply custom styling
style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", fieldbackground="#2E2E2E", background="#2E2E2E", foreground="#FFFFFF", selectbackground="#3E3E3E", selectforeground="#FFFFFF", font=("Arial", 10))
style.configure("TButton", background="#3E3E3E", foreground="#FFFFFF", font=("Arial", 10, "bold"))
style.map("TButton", background=[('active', '#4E4E4E')])

# Global variables
video_info = None
thumbnail_label = None

# Create main frame
main_frame = Frame(root, bg="#1E1E1E", bd=2, relief="flat")
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# URL input and Load button row
url_frame = Frame(main_frame, bg="#1E1E1E")
url_frame.pack(fill="x", pady=10)

url_label = Label(url_frame, text="YouTube URL:", font=("Arial", 12, "bold"), fg="#FFFFFF", bg="#1E1E1E")
url_label.pack(side=LEFT, padx=(0, 10))

url_entry = Entry(url_frame, width=50, font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF", insertbackground="#FFFFFF", borderwidth=1, relief="solid")
url_entry.pack(side=LEFT, padx=(0, 10), ipady=7)

load_button = Button(url_frame, text="Load Video", font=("Arial", 10, "bold"), bg="#3E3E3E", fg="#FFFFFF", activebackground="#4E4E4E", relief="flat", command=lambda: load_video())
load_button.pack(side=LEFT)

# Video info and thumbnail frame
info_frame = Frame(main_frame, bg="#1E1E1E")
info_frame.pack(fill="x", pady=10)

video_title = Label(info_frame, text="", font=("Arial", 11, "bold"), fg="#FFFFFF", bg="#1E1E1E", wraplength=600)
video_title.pack(anchor="w", pady=5)

# Format and Resolution selection
options_frame = Frame(main_frame,

 bg="#1E1E1E")
options_frame.pack(pady=10)

# Format selection
format_label = Label(options_frame, text="Format:", font=("Arial", 12, "bold"), fg="#FFFFFF", bg="#1E1E1E")
format_label.grid(row=0, column=0, padx=(0, 10), pady=5)

format_var = StringVar(value="MP4")
format_combobox = ttk.Combobox(options_frame, textvariable=format_var, state="readonly", width=10, values=["MP4", "MP3"], font=("Arial", 10))
format_combobox.grid(row=0, column=1, padx=10, pady=5)

# Resolution selection
resolution_label = Label(options_frame, text="Resolution:", font=("Arial", 12, "bold"), fg="#FFFFFF", bg="#1E1E1E")
resolution_label.grid(row=0, column=2, padx=(20, 10), pady=5)

resolution_var = StringVar()
resolution_combobox = ttk.Combobox(options_frame, textvariable=resolution_var, state="readonly", width=15, font=("Arial", 10))
resolution_combobox.grid(row=0, column=3, padx=10, pady=5)

# Status label
status_frame = Frame(main_frame, bg="#1E1E1E")
status_frame.pack(fill="x", pady=20)

status_label = Label(status_frame, text="", font=("Arial", 10), fg="#BBBBBB", bg="#1E1E1E")
status_label.pack(pady=5)

# Download and Retry buttons
button_frame = Frame(main_frame, bg="#1E1E1E")
button_frame.pack(pady=20)

download_button = Button(button_frame, text="Download", font=("Arial", 12, "bold"), bg="#4CAF50", fg="#FFFFFF", activebackground="#45A049", relief="flat", command=lambda: download_video(), state=DISABLED, width=15)
download_button.pack(side=LEFT, padx=10)

retry_button = Button(button_frame, text="Retry", font=("Arial", 12, "bold"), bg="#3E3E3E", fg="#FFFFFF", activebackground="#4E4E4E", relief="flat", command=lambda: load_video(), state=DISABLED, width=15)
retry_button.pack(side=LEFT, padx=10)

# Function to load and display thumbnail
def load_thumbnail(url):
    global thumbnail_label
    try:
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        image = image.resize((120, 90), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        if thumbnail_label:
            thumbnail_label.destroy()
        thumbnail_label = Label(info_frame, image=photo, bg="#1E1E1E")
        thumbnail_label.image = photo  # Keep a reference
        thumbnail_label.pack(anchor="w", pady=5)
    except Exception as e:
        status_label.config(text=f"Failed to load thumbnail: {str(e)}")

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
        download_button.config(state=DISABLED)
        retry_button.config(state=DISABLED)
        # Clean the URL
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

        # Fetch video info
        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            video_info = info

        # Display title and thumbnail
        video_title.config(text=info.get('title', 'Unknown Title'))
        thumbnail_url = info.get('thumbnail')
        if thumbnail_url:
            threading.Thread(target=load_thumbnail, args=(thumbnail_url,), daemon=True).start()

        # Extract resolutions
        formats = info.get('formats', [])
        resolutions = []
        for fmt in formats:
            height = fmt.get('height')
            if height:
                resolution = f"{height}p"
                if resolution not in resolutions:
                    resolutions.append(resolution)

        # Sort resolutions
        resolutions.sort(key=lambda x: int(x[:-1]), reverse=True)
        resolution_combobox['values'] = resolutions
        if resolutions:
            resolution_var.set(resolutions[0])
            download_button.config(state=NORMAL)
            status_label.config(text="Video loaded successfully")
        else:
            messagebox.showerror("Error", "No video streams available")
            status_label.config(text="")
            retry_button.config(state=NORMAL)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load video: {str(e)}")
        status_label.config(text="")
        retry_button.config(state=NORMAL)
    finally:
        load_button.config(state=NORMAL)

# Function to perform the download
def perform_download(resolution, save_path, format_type):
    try:
        status_label.config(text=f"Downloading {format_type}...")
        ydl_opts = {
            'outtmpl': save_path,
        }
        if format_type == "MP4":
            ydl_opts['format'] = f'bestvideo[height<={resolution[:-1]}]+bestaudio/best[height<={resolution[:-1]}]'
            ydl_opts['merge_output_format'] = 'mp4'
        else:  # MP3
            ydl_opts['format'] = 'bestaudio'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_info['webpage_url']])
        root.after(0, lambda: messagebox.showinfo("Success", "Download completed"))
        root.after(0, lambda: status_label.config(text="Download completed"))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
        root.after(0, lambda: status_label.config(text="Download failed"))
        root.after(0, lambda: retry_button.config(state=NORMAL))
    finally:
        root.after(0, lambda: download_button.config(text="Download", state=NORMAL))

# Function to handle the download process
def download_video():
    global video_info
    if video_info is None:
        messagebox.showerror("Error", "Please load a video first")
        return
    resolution = resolution_var.get()
    format_type = format_var.get()
    if not resolution and format_type == "MP4":
        messagebox.showerror("Error", "Please select a resolution")
        return
    save_path = filedialog.asksaveasfilename(
        defaultextension=f".{format_type.lower()}",
        filetypes=[(f"{format_type} files", f"*.{format_type.lower()}")],
        initialfile=video_info.get('title', 'video')
    )
    if save_path:
        download_button.config(text="Downloading...", state=DISABLED)
        retry_button.config(state=DISABLED)
        threading.Thread(target=perform_download, args=(resolution, save_path, format_type), daemon=True).start()

# Start the main loop
root.mainloop()