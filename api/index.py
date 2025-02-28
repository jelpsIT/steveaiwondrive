from flask import Flask, request, redirect, url_for, render_template, send_file
import os
import time
from slugify import slugify
import random
import requests

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SONG_FILE'] = 'song.mp3'
TRANSFER_SH_URL = "https://transfer.sh"

song_titles = [
    "superstition", "i-just-called-to-say-i-love-you", "isn't-she-lovely",
    "higher-ground", "sir-duke", "living-for-the-city", "love's-in-need-of-love-today",
    "master-blaster", "overjoyed", "rocket-love", "too-high"
]

def get_random_title():
    return random.choice(song_titles)

def save_file(title, file):
    title_slug = slugify(title)
    timestamp = int(time.time())
    file_extension = file.filename.split('.')[-1]
    file_name = f"{title_slug}-{timestamp}.{file_extension}"
    # Save temporarily to /tmp
    temp_path = f"/tmp/{file_name}"
    file.save(temp_path)
    # Upload to Transfer.sh
    with open(temp_path, 'rb') as f:
        response = requests.put(f"{TRANSFER_SH_URL}/{file_name}", data=f)
        response.raise_for_status()
        url = response.text.strip()
    os.remove(temp_path)  # Clean up
    return url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
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

@app.route('/download/<path:file_name>')
def download_file(file_name):
    return "Downloads not supported directly; use the provided Transfer.sh link.", 200

if __name__ == '__main__':
    app.run(debug=True)