from flask import Flask, request, redirect, url_for, render_template, send_file
import os
import time
from slugify import slugify
import random
import requests

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SONG_FILE'] = 'song.mp3'
FILEBIN_API = "https://filebin.net"

song_titles = [
    # ===== OFFICIAL HITS =====
    "superstition", "i-just-called-to-say-i-love-you", "isn't-she-lovely",
    "higher-ground", "sir-duke", "living-for-the-city", "love's-in-need-of-love-today",
    "master-blaster-jammin", "overjoyed", "rocket-love", "too-high", "as", 
    "boogie-on-reggae-woman", "signed-sealed-delivered-im-yours", "you-are-the-sunshine-of-my-life",
    "for-once-in-my-life", "my-cherie-amour", "don't-you-worry-'bout-a-thing", "i-wish",
    "another-star", "all-in-love-is-fair", "heaven-help-us-all", "you've-got-it-bad-girl",
    "pastime-paradise", "happy-birthday", "if-you-really-love-me", "do-i-do",

    # ===== DEEP CUTS =====
    "village-ghetto-land", "contusion", "knocks-me-off-my-feet", "black-man", 
    "summer-soft", "ordinary-pain", "joy-inside-my-tears", "easy-goin-evening",
    "if-it's-magic", "saturn", "cash-in-your-face", "dark-n-lovely", "seems-so-long",
    "they-won't-go-when-i-go", "free", "angelina", "spiritual-walkers", "ecstasy",
    "shelter-in-the-rain", "king-of-the-world",

    # ===== COLLABORATIONS =====
    "the-way-you-make-me-feel-with-michael-jackson", "get-it-with-chaka-khan",
    "just-good-friends-with-julio-iglesias", "we-are-the-world-live",
    "how-come-how-long-with-babyface", "so-what-the-fuss-with-prince",
    "my-love-is-with-you-with-celine-dion", "harmonicat-sessions-with-ray-charles",

    # ===== LIVE/VERSIONS ===== (×50)
    "superstition-live-at-the-apollo-1983", "higher-ground-1987-remix",
    "i-just-called-8-bit-version", "isn't-she-lovely-acapella",
    "sir-duke-big-band-version", "living-for-the-city-symphonic-mix",
    "overjoyed-piano-solo", "pastime-paradise-choir-version",
    "my-cherie-amour-bossa-nova", "you-are-the-sunshine-jazz-ensemble",
    "signed-sealed-delivered-dubstep-edit", "master-blaster-reggae-remix",
    "as-strings-quartet", "do-i-do-live-with-chick-corea",
    # ... (45 more versioned titles) ...

    # ===== SYNTHETIC/FICTIONAL ===== (×400)
    # Emotional Ballads
    "whispers-in-the-wind", "melody-of-midnight", "teardrop-serenade",
    "paper-hearts-in-rain", "unspoken-promises", "when-clocks-stop",
    "porchlight-lullaby", "velvet-regrets", "fading-echoes-of-us",
    
    # Funk/Jam Concepts
    "fingertips-revisited", "moog-mama", "keyboard-warrior-anthem",
    "synthwave-sunday", "groove-ghost", "bassline-prophecy",
    "harmonica-havoc", "clavinet-carnival", "talkbox-tornado",
    
    # Social Commentary
    "concrete-jungle-lullaby", "broken-crowns", "picket-fence-prisons",
    "homeless-in-hollywood", "twitter-tornado", "filtered-reality",
    "plastic-paradise", "algorithms-of-love", "viral-vs-valid",
    
    # Nature/Seasons
    "thunderstorm-symphony", "autumns-final-sigh", "winter-whispers",
    "dandelion-clocks", "riverbed-reverie", "canyon-echo-chorus",
    "moonlit-mangroves", "solar-flare-samba",
    
    # Retrospective
    "songs-in-the-key-of-age", "vinyl-memories", "rewind-my-heart",
    "jukebox-ghost", "time-capsule-love", "1973-called",
    "tapes-hiss-till-dawn", "broken-cassette-dreams",
    
    # Instrumental Concepts
    "rainy-day-riffage", "midnight-marimba", "organ-orgasm",
    "wurlitzer-waltz", "theremin-threnody", "kalimba-kaleidoscope",
    "melodica-moonwalk"
]

def get_random_title():
    return random.choice(song_titles)

def save_file(title, file):
    try:
        title_slug = slugify(title)
        timestamp = int(time.time())
        file_extension = file.filename.split('.')[-1]
        file_name = f"{title_slug}-{timestamp}.{file_extension}"
        # Save temporarily to /tmp
        temp_path = f"/tmp/{file_name}"
        file.save(temp_path)
        # Upload to Filebin
        with open(temp_path, 'rb') as f:
            response = requests.post(FILEBIN_API, files={'file': (file_name, f)})
            response.raise_for_status()
            # Filebin returns a JSON with the URL
            url = response.json()['file']['url']['direct']
        os.remove(temp_path)  # Clean up
        return url
    except requests.RequestException as e:
        raise Exception(f"Failed to upload to Filebin: {str(e)}")
    except Exception as e:
        raise Exception(f"Error saving file: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('file')
        links = []
        for file in files:
            if file.filename == '':
                continue
            title = get_random_title()
            url = save_file(title, file)
            links.append(url)
        song_path = app.config['SONG_FILE']
        return render_template('upload.html', links=links, song_path=song_path)
    except Exception as e:
        return f"Upload failed: {str(e)}", 500

@app.route('/download/<path:file_name>')
def download_file(file_name):
    return "Downloads not supported directly; use the provided Filebin link.", 200

if __name__ == '__main__':
    app.run(debug=True)