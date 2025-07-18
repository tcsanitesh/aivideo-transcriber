# utils.py

import os
from groq import Groq

def allowed_file(filename):
    return filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks for embedding.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def generate_video_metadata(transcript, groq_api_key=None):
    """
    Use Groq API to generate title, description, keywords, and category from transcript.
    """
    if groq_api_key is None:
        groq_api_key = os.getenv("GROK_API_KEY")
    if not groq_api_key:
        return ("[Error: GROK_API_KEY not set]",) * 4
    prompt = (
        "Transcript Summary: " + transcript +
        "\nHelp me Generate a \nTitle:, \n\nDescription:{summarization of transcript}, \nKeywords :, and \nCategory: for a promotional material based on the given transcript:\n"
        "Note: The reference of \"Tiki Well\" is actually \"TQL\" if any which is a logistic company."
    )
    try:
        client = Groq(api_key=groq_api_key)
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Only answer using the provided transcript. If the answer is not in the transcript, say 'I don't know.'"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.2
        )
        content = response.choices[0].message.content
        if content is None:
            return ("[Groq API error: No content returned]",) * 4
        generated_text = content.strip()
        lines = [l for l in generated_text.split('\n') if l.strip()]
        title = lines[0] if len(lines) > 0 else ""
        description = lines[1] if len(lines) > 1 else ""
        keywords = lines[2] if len(lines) > 2 else ""
        category = lines[3] if len(lines) > 3 else ""
        return title, description, keywords, category
    except Exception as e:
        return (f"[Groq API error: {e}]",) * 4
