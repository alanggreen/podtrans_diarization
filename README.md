# 🎙️ Podcast Transcriber & Diarizer

An automated pipeline to transcribe MP3 files, identify different speakers (diarization), and stream real-time progress to a web interface. This system is designed to bridge a **Wix Admin Page** with a **Python Backend on Render**.



## ✨ Features
- **Speaker Diarization**: Uses Google Cloud Speech-to-Text (V1) to distinguish between multiple voices.
- **Real-time Terminal**: Streams "print" logs from the Python script directly to your Wix page via Socket.io.
- **Headless Processing**: Runs transcription in a background thread to prevent web timeouts.
- **Wix Integrated**: Includes custom Velo and HTML code for a seamless admin dashboard experience.

## 🛠️ Backend Setup (Render)

### 1. Requirements
Ensure your repository contains:
- `main.py`: The Flask/SocketIO server.
- `podtrans_diarization.py`: The transcription logic.
- `requirements.txt`: Python dependencies (Flask, Gunicorn, Google-Cloud-Speech, etc.).

### 2. Environment Variables
Add the following in your Render Dashboard:
- `GOOGLE_APPLICATION_CREDENTIALS`: The **entire content** of your Google Cloud JSON key file.
- `PROJECT_ID`: Your Google Cloud Project ID.

### 3. Start Command
Use the following command to support WebSockets:
```bash
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 main:app
