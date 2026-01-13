#!/usr/bin/env python3

import re
import os

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
    """Generate filename slug from artist and title"""
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

    # Generate color scheme based on artist name
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
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

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

        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.3em;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

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

        .video-container {{
            margin: 30px 0;
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }}

        .video-wrapper {{
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
        }}

        .video-wrapper iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }}

        .markers-section {{
            margin: 40px 0;
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
        }}

        .markers-section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.4em;
        }}

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

        .marker-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            background: #fffbfb;
        }}

        .marker-time {{
            color: {color1};
            font-weight: bold;
            font-size: 1.1em;
            min-width: 60px;
            flex-shrink: 0;
        }}

        .marker-text {{
            color: #555;
            line-height: 1.6;
        }}

        .streaming-links {{
            margin-top: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
        }}

        .streaming-links h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}

        .links-container {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

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

        .stream-link:hover {{
            background: {color1};
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2em;
            }}

            .content {{
                padding: 20px;
            }}
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
            <div class="description">
                {description}
            </div>

            <div class="video-container">
                <div class="video-wrapper">
                    <iframe id="youtube-player"
                        src="https://www.youtube.com/embed/{video_id}?enablejsapi=1"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                        allowfullscreen>
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
            player = new YT.Player('youtube-player', {{
                events: {{
                    'onReady': onPlayerReady
                }}
            }});
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

def main():
    print('\n🎵 Add New Song to Your Collection\n')
    print('================================\n')

    # Get basic info
    title = input('Song Title: ')
    artist = input('Artist: ')
    youtube_url = input('YouTube URL: ')

    video_id = extract_youtube_id(youtube_url)
    if not video_id:
        print('❌ Invalid YouTube URL!')
        return

    description = input('Description (50-60 words): ')

    # Get markers
    print('\n--- Timestamps & Annotations ---')
    markers = []

    while True:
        time = input(f'Timestamp #{len(markers) + 1} (mm:ss or leave empty to finish): ')

        if not time:
            if len(markers) == 0:
                print('❌ You need at least one marker!')
                continue
            break

        text = input('What to listen for: ')
        markers.append({
            'time': time,
            'seconds': time_to_seconds(time),
            'text': text
        })

    # Get streaming links
    print('\n--- Streaming Links (optional) ---')
    spotify_link = input('Spotify Link (or press Enter to skip): ')
    apple_music_link = input('Apple Music Link (or press Enter to skip): ')
    youtube_music_link = input('YouTube Music Link (or press Enter to skip): ')

    # Generate filename
    filename = generate_slug(artist, title) + '.html'
    filepath = os.path.join(os.path.dirname(__file__), filename)

    # Generate HTML
    html = generate_html({
        'title': title,
        'artist': artist,
        'videoId': video_id,
        'description': description,
        'markers': markers,
        'links': {
            'spotify': spotify_link,
            'appleMusic': apple_music_link,
            'youtubeMusic': youtube_music_link
        }
    })

    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'\n✅ Song page created: {filename}')
    print('\nNext steps:')
    print(f'1. Run: git add {filename}')
    print(f'2. Run: git commit -m "Add {title} by {artist}"')
    print('3. Run: git push')
    print('4. Update index.html to add a link to this song')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n❌ Cancelled')
    except Exception as e:
        print(f'\n❌ Error: {e}')
