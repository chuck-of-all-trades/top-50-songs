#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function question(prompt) {
    return new Promise((resolve) => {
        rl.question(prompt, resolve);
    });
}

function timeToSeconds(timeStr) {
    const parts = timeStr.split(':');
    if (parts.length === 2) {
        const mins = parseInt(parts[0]) || 0;
        const secs = parseInt(parts[1]) || 0;
        return mins * 60 + secs;
    }
    return 0;
}

function extractYouTubeId(url) {
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\?\/]+)/,
        /^([a-zA-Z0-9_-]{11})$/
    ];

    for (let pattern of patterns) {
        const match = url.match(pattern);
        if (match) return match[1];
    }
    return null;
}

function generateSlug(artist, title) {
    return (artist + '-' + title)
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
}

function generateHTML(data) {
    const { title, artist, videoId, description, markers, links } = data;

    // Generate markers HTML
    let markersHtml = '';
    for (let marker of markers) {
        markersHtml += `
                <div class="marker-item" data-time="${marker.seconds}">
                    <span class="marker-time">${marker.time}</span>
                    <span class="marker-text">${marker.text}</span>
                </div>`;
    }

    // Generate streaming links HTML
    let streamingLinksHtml = `
                    <a href="https://www.youtube.com/watch?v=${videoId}" target="_blank" class="stream-link">YouTube</a>`;

    if (links.spotify) {
        streamingLinksHtml += `\n                    <a href="${links.spotify}" target="_blank" class="stream-link">Spotify</a>`;
    }
    if (links.appleMusic) {
        streamingLinksHtml += `\n                    <a href="${links.appleMusic}" target="_blank" class="stream-link">Apple Music</a>`;
    }
    if (links.youtubeMusic) {
        streamingLinksHtml += `\n                    <a href="${links.youtubeMusic}" target="_blank" class="stream-link">YouTube Music</a>`;
    }

    // Generate color scheme based on artist name
    const colors = [
        ['#8b0000', '#2d1b2e'],
        ['#667eea', '#764ba2'],
        ['#f093fb', '#f5576c'],
        ['#4facfe', '#00f2fe'],
        ['#43e97b', '#38f9d7']
    ];
    const colorIndex = artist.length % colors.length;
    const [color1, color2] = colors[colorIndex];

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} - ${artist}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, ${color2} 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, ${color1} 0%, ${color2} 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.3em;
            opacity: 0.9;
        }

        .content {
            padding: 40px;
        }

        .description {
            font-size: 1.1em;
            line-height: 1.8;
            color: #333;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid ${color1};
        }

        .video-container {
            margin: 30px 0;
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }

        .video-wrapper {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
        }

        .video-wrapper iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }

        .markers-section {
            margin: 40px 0;
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
        }

        .markers-section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.4em;
        }

        .marker-item {
            background: white;
            padding: 18px;
            margin-bottom: 12px;
            border-radius: 8px;
            border-left: 4px solid ${color1};
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: flex-start;
            gap: 15px;
        }

        .marker-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            background: #fffbfb;
        }

        .marker-time {
            color: ${color1};
            font-weight: bold;
            font-size: 1.1em;
            min-width: 60px;
            flex-shrink: 0;
        }

        .marker-text {
            color: #555;
            line-height: 1.6;
        }

        .streaming-links {
            margin-top: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .streaming-links h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
        }

        .links-container {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .stream-link {
            display: inline-block;
            padding: 12px 24px;
            background: white;
            color: ${color1};
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
            border: 2px solid ${color1};
        }

        .stream-link:hover {
            background: ${color1};
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }

            .content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>${title}</h1>
            <p>${artist}</p>
        </div>

        <div class="content">
            <div class="description">
                ${description}
            </div>

            <div class="video-container">
                <div class="video-wrapper">
                    <iframe id="youtube-player"
                        src="https://www.youtube.com/embed/${videoId}?enablejsapi=1"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>

            <div class="markers-section">
                <h2>Key Moments to Listen For:</h2>
${markersHtml}
            </div>

            <div class="streaming-links">
                <h3>Listen On:</h3>
                <div class="links-container">
${streamingLinksHtml}
                </div>
            </div>
        </div>
    </div>

    <script src="https://www.youtube.com/iframe_api"></script>
    <script>
        let player;

        function onYouTubeIframeAPIReady() {
            player = new YT.Player('youtube-player', {
                events: {
                    'onReady': onPlayerReady
                }
            });
        }

        function onPlayerReady(event) {
            document.querySelectorAll('.marker-item').forEach(item => {
                item.addEventListener('click', function() {
                    const time = parseInt(this.dataset.time);
                    player.seekTo(time, true);
                    player.playVideo();
                });
            });
        }
    </script>
</body>
</html>`;
}

async function main() {
    console.log('\n🎵 Add New Song to Your Collection\n');
    console.log('================================\n');

    // Get basic info
    const title = await question('Song Title: ');
    const artist = await question('Artist: ');
    const youtubeUrl = await question('YouTube URL: ');

    const videoId = extractYouTubeId(youtubeUrl);
    if (!videoId) {
        console.log('❌ Invalid YouTube URL!');
        rl.close();
        return;
    }

    const description = await question('Description (50-60 words): ');

    // Get markers
    console.log('\n--- Timestamps & Annotations ---');
    const markers = [];
    let addMore = true;

    while (addMore) {
        const time = await question(`Timestamp #${markers.length + 1} (mm:ss or leave empty to finish): `);

        if (!time) {
            if (markers.length === 0) {
                console.log('❌ You need at least one marker!');
                continue;
            }
            addMore = false;
        } else {
            const text = await question('What to listen for: ');
            markers.push({
                time: time,
                seconds: timeToSeconds(time),
                text: text
            });
        }
    }

    // Get streaming links
    console.log('\n--- Streaming Links (optional) ---');
    const spotifyLink = await question('Spotify Link (or press Enter to skip): ');
    const appleMusicLink = await question('Apple Music Link (or press Enter to skip): ');
    const youtubeMusicLink = await question('YouTube Music Link (or press Enter to skip): ');

    // Generate filename
    const filename = generateSlug(artist, title) + '.html';
    const filepath = path.join(__dirname, filename);

    // Generate HTML
    const html = generateHTML({
        title,
        artist,
        videoId,
        description,
        markers,
        links: {
            spotify: spotifyLink,
            appleMusic: appleMusicLink,
            youtubeMusic: youtubeMusicLink
        }
    });

    // Save file
    fs.writeFileSync(filepath, html);

    console.log(`\n✅ Song page created: ${filename}`);
    console.log('\nNext steps:');
    console.log('1. Run: git add ' + filename);
    console.log('2. Run: git commit -m "Add ' + title + ' by ' + artist + '"');
    console.log('3. Run: git push');
    console.log('4. Update index.html to add a link to this song');

    rl.close();
}

main().catch(err => {
    console.error('Error:', err);
    rl.close();
});
