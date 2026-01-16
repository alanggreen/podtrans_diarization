import os
import requests
import threading
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from podtrans_diarization import transcribe_podcast

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def socket_log(msg):
    socketio.emit('log_update', {'msg': msg})

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    # We now expect a URL instead of a raw file to avoid memory spikes
    file_url = data.get('file_url')
    file_name = data.get('file_name')

    if not file_url:
        return jsonify({"error": "No URL provided"}), 400

    save_path = os.path.join("/tmp", file_name)
    out_path = save_path.replace(".mp3", ".txt")

    def run_task():
        try:
            socket_log("📥 Fetching audio file from Wix...")
            # Convert Wix internal URL to a public-facing one if necessary
            download_url = file_url.replace('wix:static/v1/', 'https://static.wixstatic.com/media/')
            
            response = requests.get(download_url, stream=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            socket_log("🛠 Starting Segmented Transcription...")
            transcribe_podcast(save_path, out_path, socket_log)
            socketio.emit('finished', {'file_name': os.path.basename(out_path)})
        except Exception as e:
            socket_log(f"❌ Error: {str(e)}")

    threading.Thread(target=run_task).start()
    return jsonify({"status": "Accepted"}), 202

# ... (keep your /download route)
