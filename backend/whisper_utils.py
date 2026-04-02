import os
import subprocess
import tempfile
import requests
from pydub import AudioSegment
from config import GROQ_API_KEY

CHUNK_DURATION_MS = 10 * 60 * 1000  # 10 minutes
CHUNK_DIR = "audio_chunks"

def transcribe_video(video_path):
    print(f"⚙️ [transcribe_video] Transcribing audio for: {video_path}")
    
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    chunk_folder = os.path.join(CHUNK_DIR, video_name)
    os.makedirs(chunk_folder, exist_ok=True)

    # 1. Extract full audio
    temp_audio_path = os.path.join(chunk_folder, f"{video_name}.wav")
    ffmpeg_cmd = ["ffmpeg", "-y", "-i", video_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", temp_audio_path]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if not os.path.exists(temp_audio_path) or os.path.getsize(temp_audio_path) == 0:
        print("❌ [transcribe_video] Audio extraction failed: empty file")
        return []

    print("🔪 Splitting audio into chunks...")
    audio = AudioSegment.from_wav(temp_audio_path)
    duration_ms = len(audio)
    subtitles = []

    for i in range(0, duration_ms, CHUNK_DURATION_MS):
        chunk = audio[i:i + CHUNK_DURATION_MS]
        chunk_index = i // CHUNK_DURATION_MS
        chunk_path = os.path.join(chunk_folder, f"chunk_{chunk_index}.wav")
        chunk.export(chunk_path, format="wav")

        print(f"📤 Uploading chunk {chunk_index + 1}...")

        with open(chunk_path, "rb") as f:
            resp = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files={"file": f},
                data={"model": "whisper-large-v3", "response_format": "verbose_json"}
            )

        if resp.status_code != 200:
            print(f"❌ Whisper API error (chunk {chunk_index}): {resp.text}")
            continue

        result = resp.json()
        for seg in result.get("segments", []):
            seg["start"] += (i / 1000)  # adjust time
            seg["end"] += (i / 1000)
            subtitles.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"]
            })

        os.remove(chunk_path)

    os.remove(temp_audio_path)
    print(f"✅ [transcribe_video] Segments merged: {len(subtitles)}")

    return subtitles
