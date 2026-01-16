import os
from pydub import AudioSegment
from google.cloud import speech

# Diarization settings
MIN_SPEAKERS = 2
MAX_SPEAKERS = 2

def transcribe_segment(client, content, sample_rate, log_func):
    audio = speech.RecognitionAudio(content=content)
    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=MIN_SPEAKERS,
        max_speaker_count=MAX_SPEAKERS,
    )
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code="en-US",
        diarization_config=diarization_config,
        model="video",
    )

    try:
        response = client.recognize(config=config, audio=audio)
    except Exception as e:
        log_func(f"   ❌ API Error: {e}")
        return ""

    if not response.results: return ""
    result = response.results[-1]
    if not result.alternatives or not result.alternatives[0].words: return ""

    words_info = result.alternatives[0].words
    transcript_lines = []
    current_speaker = None
    current_sentence = []

    for word_info in words_info:
        speaker_tag = word_info.speaker_tag
        if current_speaker is not None and current_speaker != speaker_tag:
            transcript_lines.append(f"Voice {current_speaker}: {' '.join(current_sentence)}")
            current_sentence = []
        current_speaker = speaker_tag
        current_sentence.append(word_info.word)

    if current_speaker and current_sentence:
        transcript_lines.append(f"Voice {current_speaker}: {' '.join(current_sentence)}")

    return "\n".join(transcript_lines)

def transcribe_podcast(mp3_file_path, output_text_file, log_func):
    client = speech.SpeechClient()
    log_func(f"🎧 Loading: {os.path.basename(mp3_file_path)}")
    
    audio = AudioSegment.from_file(mp3_file_path).set_channels(1).set_frame_rate(16000)
    chunk_length_ms = 50 * 1000 
    num_chunks = len(audio) // chunk_length_ms + 1
    full_transcription = []
    
    for i in range(num_chunks):
        log_func(f"⏳ Processing chunk {i+1}/{num_chunks}...")
        start_ms = i * chunk_length_ms
        end_ms = min((i + 1) * chunk_length_ms, len(audio))
        chunk = audio[start_ms:end_ms]
        if len(chunk) < 1000: continue

        chunk_content = chunk.export(format="wav").read()
        chunk_text = transcribe_segment(client, chunk_content, 16000, log_func)
        if chunk_text:
            full_transcription.append(chunk_text)

    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write("\n".join(full_transcription))
