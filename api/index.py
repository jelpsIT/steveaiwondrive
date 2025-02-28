from flask import Flask, request, redirect, url_for, render_template, send_file
import os
import time
from slugify import slugify
import random

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SONG_FILE'] = 'song.mp3'

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
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(file_path)
    return file_name

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
        file_name = save_file(title, file)
        link = url_for('download_file', file_name=file_name, _external=True)
        links.append(link)
    song_path = app.config['SONG_FILE']
    return render_template('upload.html', links=links, song_path=song_path)

@app.route('/download/<path:file_name>')
def download_file(file_name):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "File not found", 404

# Vercel requires this to work as a serverless function
if __name__ == '__main__':
    app.run()
else:
    # Export Flask app as a WSGI application for Vercel
    from wsgi import application
    app.wsgi_app = application