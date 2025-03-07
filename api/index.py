from flask import Flask, request, redirect, url_for, render_template, send_file
import os
import time
from slugify import slugify
import random
import vercel_blob import put

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SONG_FILE'] = 'song.mp3'

# Check for BLOB_READ_WRITE_TOKEN at startup
blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
if not blob_token:
    raise ValueError("BLOB_READ_WRITE_TOKEN environment variable is not set")

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
        file_extension = file.filename.rsplit('.', 1)[-1].lower()
        file_name = f"{title_slug}-{timestamp}.{file_extension}"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            temp_path = temp_file.name
            temp_file.write(file.read())
            temp_file.flush()
            temp_file.seek(0)
            file_content = temp_file.read()
        
        blob = put(file_name, file_content, token=blob_token, access='public')
        
        os.remove(temp_path)
        return blob['url'], timestamp
    
    except Exception as e:
        raise Exception(f"Error saving file to Vercel Blob: {str(e)}")


@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading index: {str(e)}", 500


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('file')
        if not files or all(file.filename == '' for file in files):
            return "No files uploaded", 400
        
        links = []
        for file in files:
            if file.filename == '':
                continue
            title = get_random_title()
            url, timestamp = save_file(title, file)
            links.append({'url': url, 'timestamp': timestamp})
        
        song_path = app.config['SONG_FILE']
        return render_template('upload.html', links=links, song_path=song_path)
    
    except Exception as e:
        return f"Upload failed: {str(e)}", 500


@app.route('/download/<path:file_name>')
def download_file(file_name):
    return "Use the provided Vercel Blob link directly.", 200


# Jinja2 filter for timestamp formatting
from datetime import datetime
app.jinja_env.filters['datetime'] = lambda ts: datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    app.run(debug=True)