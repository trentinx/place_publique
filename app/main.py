from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from pathlib import Path
from place_publique.config import Config
import os

app = Flask(__name__)
CORS(app)

# Configure template folder
app.template_folder = os.path.join(os.path.dirname(__file__), 'templates')

# Calculate absolute path to captures directory
frontend_dir = Path(__file__).parent.resolve()
config_path = frontend_dir.parent / "config.yaml"
config = Config(config_path)

project_root = frontend_dir.parent
captures_dir = project_root / "captures"


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html', interval=config.scraping_interval * 1000)  # Refresh every x * 1000 ms (x second)


@app.route('/health')
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.route('/images/<path:filename>')
def serve_images(filename):
    """Serve images from captures directory."""
    return send_from_directory(str(captures_dir), filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

