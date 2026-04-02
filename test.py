import requests
import os

# Replace with your actual API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")

# Groq endpoint
url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "user", "content": "Hello, are you working?"}
    ],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=payload)

# Output result
print("Status Code:", response.status_code)
try:
    print("Response:", response.json())
except:
    print("Raw response:", response.text)
