from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from whisper_utils import transcribe_video
from chroma_utils import store_transcripts, query_chroma, delete_video_data, client, embedding_func
from llama_utils import generate_response
from video_utils import get_video_clip_url
from fastapi.staticfiles import StaticFiles  # ✅
import os
from typing import List
from fastapi.responses import JSONResponse
import requests  # ✅
from config import GROQ_API_KEY, GROQ_MODEL  # ✅

import queue
import threading

# ✅ Background task queue (in-memory)
transcription_queue = queue.Queue()

def transcription_worker():
    while True:
        path, filename = transcription_queue.get()
        try:
            print("⚙️ [process_transcription] Running for:", filename)
            srt_data = transcribe_video(path)
            print(f"📄 [process_transcription] Subtitles received: {len(srt_data)}")
            store_transcripts(filename, srt_data)
        except Exception as e:
            print(f"❌ Error in transcription_worker: {e}")
        transcription_queue.task_done()

# ✅ Start the worker thread
threading.Thread(target=transcription_worker, daemon=True).start()

app = FastAPI()

UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploaded_videos", StaticFiles(directory=UPLOAD_DIR), name="uploaded_videos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_files(
    files: List[UploadFile] = File(...)
):
    for file in files:
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        save_dir = os.path.dirname(save_path)
        os.makedirs(save_dir, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(await file.read())

        # ✅ Add to queue
        transcription_queue.put((save_path, file.filename))

    return {"message": "Upload received and transcription queued"}

@app.get("/list_videos/")
def list_videos():
    videos = []
    for root, _, files in os.walk(UPLOAD_DIR):
        for f in files:
            if f.lower().endswith(".mp4"):
                relative_path = os.path.relpath(os.path.join(root, f), UPLOAD_DIR)
                videos.append(relative_path.replace("\\", "/"))
    return JSONResponse(content={"videos": sorted(videos)})

@app.post("/chat/")
async def chat(prompt: str = Form(...), video: str = Form(...)):
    print(f"🛎️ [chat] Incoming request — Prompt: {prompt}")

    # ✅ Dynamically choose most relevant video using LLM
    video_list = []
    for root, _, files in os.walk(UPLOAD_DIR):
        for f in files:
            if f.lower().endswith(".mp4"):
                rel_path = os.path.relpath(os.path.join(root, f), UPLOAD_DIR)
                video_list.append(rel_path.replace("\\", "/"))

    inferred_video = infer_video_name(prompt, video_list)
    print(f"🤖 Using inferred video: {inferred_video}")

    context = query_chroma(inferred_video, prompt)
    response = generate_response(prompt, context, video_name=inferred_video)

    return {
        "answer": response,
        "source": context
    }

def infer_video_name(prompt, video_list):
    system_prompt = (
        "You're a helpful assistant. Given a list of video file names and a user query, choose the most relevant video.\n"
        "Only return **one exact video file name** from the list below. If nothing matches, return 'unknown'."
    )

    user_prompt = f"Video Files:\n" + "\n".join(video_list) + f"\n\nUser Question:\n{prompt}\n\nAnswer with exact filename only:"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1
    }

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        result = res.json()["choices"][0]["message"]["content"].strip()
        if result in video_list:
            return result
        else:
            return video_list[0] if video_list else ""
    except Exception as e:
        print("❌ LLM inference failed:", e)
        return video_list[0] if video_list else ""

@app.delete("/delete/")
def delete_file(video: str):
    delete_video_data(video)
    try:
        os.remove(os.path.join(UPLOAD_DIR, video))
    except:
        pass
    return {"status": "deleted"}

@app.get("/clip/")
def clip_video(video: str, start: float, end: float):
    video_path = os.path.join(UPLOAD_DIR, video)
    return get_video_clip_url(video_path, start, end)

@app.get("/debug_check/")
def debug_check(video: str):
    from chroma_utils import query_chroma
    return query_chroma(video, "dummy check", top_k=1)

@app.delete("/wipe_all/")
def wipe_all_collections():
    import chromadb
    from config import CHROMA_DB_DIR
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    client.reset()
    print("🧨 [wipe_all_collections] All ChromaDB collections deleted.")
    return {"status": "success", "message": "All collections wiped."}

@app.get("/debug_subtitles/")
def debug_subtitles(video: str):
    from chroma_utils import sanitize_name, client, embedding_func

    try:
        safe_name = sanitize_name(video)
        print(f"🔍 [debug_subtitles] Checking collection: {safe_name}")
        collection = client.get_or_create_collection(name=f"video_{safe_name}", embedding_function=embedding_func)

        count = collection.count()
        sample_docs = collection.peek(min(5, count))

        return {
            "collection_name": safe_name,
            "count": count,
            "sample": sample_docs
        }
    except Exception as e:
        print(f"❌ [debug_subtitles] Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/status/")
def get_transcription_status(video: str):
    from chroma_utils import sanitize_name, client, embedding_func

    try:
        collection_name = f"video_{sanitize_name(video)}"
        collection = client.get_or_create_collection(name=collection_name, embedding_function=embedding_func)
        count = collection.count()

        if count > 0:
            return {"status": "done", "count": count}
        else:
            return {"status": "processing", "count": 0}
    except Exception as e:
        return {"status": "error", "message": str(e)}
