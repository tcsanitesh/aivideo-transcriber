import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_grok():
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        print("[Error: GROK_API_KEY not set in .env]")
        return
    url = "https://api.grok.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-1",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "max_tokens": 32,
        "temperature": 0.2
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        print("Grok API response:", data['choices'][0]['message']['content'].strip())
    except Exception as e:
        print(f"[Grok API error: {e}]")

if __name__ == "__main__":
    test_grok()
