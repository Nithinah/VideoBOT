import requests
from config import GROQ_API_KEY, GROQ_MODEL

def generate_response(user_query, context_segments, video_name=None):
    if not context_segments:
        return "Sorry, the subtitles don't contain an answer to that."

    subtitle_lines = [
        f"[{seg['start']} - {seg['end']}]: {seg['subtitle']}"
        for seg in context_segments
    ]
    context_text = "\n".join(subtitle_lines)

    # ✅ Use actual video name from top subtitle segment
    video_from_context = context_segments[0].get("video", "Unknown Video")

    prompt = f"""
You are a helpful video assistant. Use the following full subtitle context to answer the user's question.
Only use what's available in the subtitles. Don't guess. Respond in **exactly this format**, with a total of **4 lines**:

Summary: <one-line natural answer>

📍 Video: {video_from_context} 
⏱ Timestamp: <start> - <end>  
🗒 Subtitle: "<best subtitle>"



Context:
{context_text}

User Question: {user_query}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You answer questions from subtitle text with timestamp and video context."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "Sorry, there was an error generating the response."
