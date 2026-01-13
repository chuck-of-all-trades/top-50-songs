#!/usr/bin/env python3
"""
Song Manager GUI - Easy interface to add songs to your collection
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
import os
import subprocess

def time_to_seconds(time_str):
    """Convert mm:ss to seconds"""
    parts = time_str.split(':')
    if len(parts) == 2:
        mins = int(parts[0]) if parts[0] else 0
        secs = int(parts[1]) if parts[1] else 0
        return mins * 60 + secs
    return 0

def extract_youtube_id(url):
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\?\/]+)',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def generate_slug(artist, title):
    """Generate filename slug"""
    slug = (artist + '-' + title).lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug

def generate_html(data):
    """Generate complete HTML page"""
    title = data['title']
    artist = data['artist']
    video_id = data['videoId']
    description = data['description']
    markers = data['markers']
    links = data['links']

    # Generate markers HTML
    markers_html = ''
    for marker in markers:
        markers_html += f"""
                <div class="marker-item" data-time="{marker['seconds']}">
                    <span class="marker-time">{marker['time']}</span>
                    <span class="marker-text">{marker['text']}</span>
                </div>"""

    # Generate streaming links HTML
    streaming_links_html = f"""
                    <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" class="stream-link">YouTube</a>"""

    if links['spotify']:
        streaming_links_html += f"""\n                    <a href="{links['spotify']}" target="_blank" class="stream-link">Spotify</a>"""
    if links['appleMusic']:
        streaming_links_html += f"""\n                    <a href="{links['appleMusic']}" target="_blank" class="stream-link">Apple Music</a>"""
    if links['youtubeMusic']:
        streaming_links_html += f"""\n                    <a href="{links['youtubeMusic']}" target="_blank" class="stream-link">YouTube Music</a>"""

    # Generate color scheme
    colors = [
        ['#8b0000', '#2d1b2e'],
        ['#667eea', '#764ba2'],
        ['#f093fb', '#f5576c'],
        ['#4facfe', '#00f2fe'],
        ['#43e97b', '#38f9d7']
    ]
    color_index = len(artist) % len(colors)
    color1, color2 = colors[color_index]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {artist}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, {color2} 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, {color1} 0%, {color2} 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.8em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .header p {{ font-size: 1.3em; opacity: 0.9; }}
        .content {{ padding: 40px; }}
        .description {{
            font-size: 1.1em;
            line-height: 1.8;
            color: #333;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid {color1};
        }}
        .video-container {{ margin: 30px 0; background: #000; border-radius: 10px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.3); }}
        .video-wrapper {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; }}
        .video-wrapper iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
        .markers-section {{ margin: 40px 0; background: #f8f9fa; padding: 30px; border-radius: 10px; }}
        .markers-section h2 {{ color: #333; margin-bottom: 20px; font-size: 1.4em; }}
        .marker-item {{
            background: white;
            padding: 18px;
            margin-bottom: 12px;
            border-radius: 8px;
            border-left: 4px solid {color1};
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: flex-start;
            gap: 15px;
        }}
        .marker-item:hover {{ transform: translateX(5px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); background: #fffbfb; }}
        .marker-time {{ color: {color1}; font-weight: bold; font-size: 1.1em; min-width: 60px; flex-shrink: 0; }}
        .marker-text {{ color: #555; line-height: 1.6; }}
        .streaming-links {{ margin-top: 30px; padding: 25px; background: #f8f9fa; border-radius: 10px; }}
        .streaming-links h3 {{ color: #333; margin-bottom: 15px; font-size: 1.2em; }}
        .links-container {{ display: flex; gap: 15px; flex-wrap: wrap; }}
        .stream-link {{
            display: inline-block;
            padding: 12px 24px;
            background: white;
            color: {color1};
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
            border: 2px solid {color1};
        }}
        .stream-link:hover {{ background: {color1}; color: white; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2em; }}
            .content {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>{artist}</p>
        </div>
        <div class="content">
            <div class="description">{description}</div>
            <div class="video-container">
                <div class="video-wrapper">
                    <iframe id="youtube-player" src="https://www.youtube.com/embed/{video_id}?enablejsapi=1"
                        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen>
                    </iframe>
                </div>
            </div>
            <div class="markers-section">
                <h2>Key Moments to Listen For:</h2>
{markers_html}
            </div>
            <div class="streaming-links">
                <h3>Listen On:</h3>
                <div class="links-container">
{streaming_links_html}
                </div>
            </div>
        </div>
    </div>
    <script src="https://www.youtube.com/iframe_api"></script>
    <script>
        let player;
        function onYouTubeIframeAPIReady() {{
            player = new YT.Player('youtube-player', {{ events: {{ 'onReady': onPlayerReady }} }});
        }}
        function onPlayerReady(event) {{
            document.querySelectorAll('.marker-item').forEach(item => {{
                item.addEventListener('click', function() {{
                    const time = parseInt(this.dataset.time);
                    player.seekTo(time, true);
                    player.playVideo();
                }});
            }});
        }}
    </script>
</body>
</html>"""

class SongManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Song Manager")
        self.root.geometry("800x700")

        # Markers list
        self.markers = []

        self.create_widgets()

    def create_widgets(self):
        # Main frame with scrollbar
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="🎵 Add New Song", font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Song Title
        ttk.Label(main_frame, text="Song Title:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Artist
        ttk.Label(main_frame, text="Artist:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.artist_entry = ttk.Entry(main_frame, width=50)
        self.artist_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # YouTube URL
        ttk.Label(main_frame, text="YouTube URL:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.youtube_entry = ttk.Entry(main_frame, width=50)
        self.youtube_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # Description
        ttk.Label(main_frame, text="Description:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.description_text = scrolledtext.ScrolledText(main_frame, width=50, height=4)
        self.description_text.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

        # Markers section
        ttk.Label(main_frame, text="Timestamps & Annotations:", font=('Arial', 12, 'bold')).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))

        # Marker input frame
        marker_frame = ttk.Frame(main_frame)
        marker_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(marker_frame, text="Time (mm:ss):").grid(row=0, column=0, padx=5)
        self.marker_time_entry = ttk.Entry(marker_frame, width=10)
        self.marker_time_entry.grid(row=0, column=1, padx=5)

        ttk.Label(marker_frame, text="Annotation:").grid(row=0, column=2, padx=5)
        self.marker_text_entry = ttk.Entry(marker_frame, width=40)
        self.marker_text_entry.grid(row=0, column=3, padx=5)

        ttk.Button(marker_frame, text="+ Add Marker", command=self.add_marker).grid(row=0, column=4, padx=5)

        # Markers list
        self.markers_listbox = tk.Listbox(main_frame, height=5, width=70)
        self.markers_listbox.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(main_frame, text="Remove Selected", command=self.remove_marker).grid(row=8, column=0, columnspan=2, pady=5)

        # Streaming links
        ttk.Label(main_frame, text="Streaming Links (optional):", font=('Arial', 12, 'bold')).grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))

        ttk.Label(main_frame, text="Spotify:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.spotify_entry = ttk.Entry(main_frame, width=50)
        self.spotify_entry.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(main_frame, text="Apple Music:").grid(row=11, column=0, sticky=tk.W, pady=5)
        self.apple_entry = ttk.Entry(main_frame, width=50)
        self.apple_entry.grid(row=11, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(main_frame, text="YouTube Music:").grid(row=12, column=0, sticky=tk.W, pady=5)
        self.ytmusic_entry = ttk.Entry(main_frame, width=50)
        self.ytmusic_entry.grid(row=12, column=1, sticky=(tk.W, tk.E), pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=13, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="✓ Create Song Page", command=self.create_song, style='Accent.TButton').grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).grid(row=0, column=1, padx=10)

        main_frame.columnconfigure(1, weight=1)

    def add_marker(self):
        time = self.marker_time_entry.get().strip()
        text = self.marker_text_entry.get().strip()

        if not time or not text:
            messagebox.showwarning("Missing Info", "Please enter both time and annotation!")
            return

        # Validate time format
        if not re.match(r'^\d+:[0-5]\d$', time):
            messagebox.showwarning("Invalid Time", "Time must be in mm:ss format (e.g., 3:45)")
            return

        self.markers.append({'time': time, 'text': text})
        self.markers_listbox.insert(tk.END, f"{time} - {text}")

        # Clear inputs
        self.marker_time_entry.delete(0, tk.END)
        self.marker_text_entry.delete(0, tk.END)

    def remove_marker(self):
        selection = self.markers_listbox.curselection()
        if selection:
            index = selection[0]
            self.markers_listbox.delete(index)
            self.markers.pop(index)

    def clear_form(self):
        if messagebox.askyesno("Clear Form", "Are you sure you want to clear all fields?"):
            self.title_entry.delete(0, tk.END)
            self.artist_entry.delete(0, tk.END)
            self.youtube_entry.delete(0, tk.END)
            self.description_text.delete('1.0', tk.END)
            self.spotify_entry.delete(0, tk.END)
            self.apple_entry.delete(0, tk.END)
            self.ytmusic_entry.delete(0, tk.END)
            self.marker_time_entry.delete(0, tk.END)
            self.marker_text_entry.delete(0, tk.END)
            self.markers_listbox.delete(0, tk.END)
            self.markers = []

    def create_song(self):
        # Validate inputs
        title = self.title_entry.get().strip()
        artist = self.artist_entry.get().strip()
        youtube_url = self.youtube_entry.get().strip()
        description = self.description_text.get('1.0', tk.END).strip()

        if not all([title, artist, youtube_url, description]):
            messagebox.showerror("Missing Info", "Please fill in all required fields!")
            return

        if not self.markers:
            messagebox.showerror("Missing Markers", "Please add at least one timestamp marker!")
            return

        video_id = extract_youtube_id(youtube_url)
        if not video_id:
            messagebox.showerror("Invalid URL", "Please enter a valid YouTube URL!")
            return

        # Prepare markers with seconds
        markers_data = []
        for marker in self.markers:
            markers_data.append({
                'time': marker['time'],
                'seconds': time_to_seconds(marker['time']),
                'text': marker['text']
            })

        # Generate HTML
        html = generate_html({
            'title': title,
            'artist': artist,
            'videoId': video_id,
            'description': description,
            'markers': markers_data,
            'links': {
                'spotify': self.spotify_entry.get().strip(),
                'appleMusic': self.apple_entry.get().strip(),
                'youtubeMusic': self.ytmusic_entry.get().strip()
            }
        })

        # Save file
        filename = generate_slug(artist, title) + '.html'
        filepath = os.path.join(os.path.dirname(__file__), filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        # Show success message
        result = messagebox.askyesno(
            "Success!",
            f"Song page created: {filename}\n\nWould you like to commit and push to GitHub now?"
        )

        if result:
            try:
                subprocess.run(['git', 'add', filename], cwd=os.path.dirname(__file__), check=True)
                subprocess.run(['git', 'commit', '-m', f'Add {title} by {artist}'], cwd=os.path.dirname(__file__), check=True)
                subprocess.run(['git', 'push'], cwd=os.path.dirname(__file__), check=True)
                messagebox.showinfo("Pushed!", "Changes have been pushed to GitHub!")
            except Exception as e:
                messagebox.showerror("Git Error", f"Error pushing to GitHub:\n{e}\n\nPlease run git commands manually.")

        # Ask if they want to clear the form
        if messagebox.askyesno("Continue?", "Would you like to add another song?"):
            self.clear_form()
        else:
            self.root.quit()

if __name__ == '__main__':
    root = tk.Tk()
    app = SongManagerGUI(root)
    root.mainloop()
