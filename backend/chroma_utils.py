import chromadb
from chromadb.utils import embedding_functions
import os
import uuid
import re
from config import CHROMA_DB_DIR

client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
embedding_func = embedding_functions.DefaultEmbeddingFunction()

def sanitize_name(name):
    name = os.path.basename(name)  # ✅ Strip folder paths like "video/"
    name = name.rsplit(".", 1)[0]
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return name[:100].strip("_")

def store_transcripts(video_name, subtitles):
    safe_name = sanitize_name(video_name)
    full_collection_name = f"video_{safe_name}"

    print(f"📦 [store_transcripts] Saving to collection: {full_collection_name}")
    print(f"📝 [store_transcripts] Subtitle count: {len(subtitles)}")

    collection = client.get_or_create_collection(name=full_collection_name, embedding_function=embedding_func)

    for i, sub in enumerate(subtitles):
        if not sub.get("text"):
            print(f"⚠️ Skipping subtitle {i} — missing 'text'")
            continue

        uid = f"{full_collection_name}_{i}_{uuid.uuid4()}"
        collection.add(
            documents=[sub["text"]],
            metadatas=[{
                "video": video_name,
                "start": sub["start"],
                "end": sub["end"],
                "subtitle": sub["text"]
            }],
            ids=[uid]
        )

def query_chroma(video_name, query_text, top_k=4):
    safe_name = sanitize_name(video_name)
    full_collection_name = f"video_{safe_name}"
    print(f"🔍 [query_chroma] Querying collection: {full_collection_name} with query: '{query_text}'")

    collection = client.get_or_create_collection(name=full_collection_name, embedding_function=embedding_func)

    # 🔁 Fetch all documents and metadata for full subtitle context
    full_data = collection.get(include=["documents", "metadatas"])

    print(f"📋 [query_chroma] Total subtitles fetched: {len(full_data['documents'])}")

    matches = []
    for doc, meta in zip(full_data['documents'], full_data['metadatas']):
        matches.append({
            "subtitle": meta["subtitle"],
            "start": seconds_to_timestamp(meta["start"]),
            "end": seconds_to_timestamp(meta["end"]),
            "video": meta["video"]
        })

    return matches


def delete_video_data(video_name):
    safe_name = sanitize_name(video_name)
    full_collection_name = f"video_{safe_name}"
    try:
        print(f"🧹 [delete_video_data] Deleting ChromaDB collection: {full_collection_name}")
        client.delete_collection(name=full_collection_name)
        print("✅ [delete_video_data] Collection deleted.")
    except Exception as e:
        print(f"❌ [delete_video_data] Failed to delete collection '{full_collection_name}': {e}")

def seconds_to_timestamp(sec):
    from datetime import timedelta
    return str(timedelta(seconds=int(sec)))
