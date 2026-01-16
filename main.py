import os
import threading
from flask import Flask, request, send_file, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from podtrans_diarization import transcribe_podcast

app = Flask(__name__)
CORS(app) # Enable Wix to talk to Render
socketio = SocketIO(app, cors_allowed_origins="*")

def socket_log(msg):
    socketio.emit('log_update', {'msg': msg})

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files: return "No file", 400
    file = request.files['file']
    path = os.path.join("/tmp", file.filename)
    file.save(path)
    out_path = path.replace(".mp3", ".txt")

    def run():
        socket_log("🚀 Starting Transcription...")
        transcribe_podcast(path, out_path, socket_log)
        socketio.emit('finished', {'file_name': os.path.basename(out_path)})

    threading.Thread(target=run).start()
    return jsonify({"status": "accepted"}), 202

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join("/tmp", filename), as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
