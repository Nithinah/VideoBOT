import os
import subprocess
from fastapi.responses import FileResponse

CLIP_DIR = "clips"
os.makedirs(CLIP_DIR, exist_ok=True)

def get_video_clip_url(video_path, start, end):
    """
    Generates a clipped video (from `start` to `end` seconds) using ffmpeg.
    Returns FastAPI FileResponse.
    """
    filename = os.path.basename(video_path)
    base, ext = os.path.splitext(filename)
    clipped_name = f"{base}_{int(start)}_{int(end)}.mp4"
    clip_path = os.path.join(CLIP_DIR, clipped_name)

    if not os.path.exists(clip_path):
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-ss", str(start),
            "-to", str(end),
            "-c:v", "libx264", "-c:a", "aac", clip_path
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return FileResponse(path=clip_path, media_type="video/mp4", filename=clipped_name)
