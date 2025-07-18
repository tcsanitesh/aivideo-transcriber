# qa_engine.py



import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def answer_query(query, context):
    """
    Call Grok API with user query and context. Returns answer string.
    """
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        return "[Error: GROK_API_KEY not set in .env]"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Only answer using the provided context. If the answer is not in the context, say 'I don't know.'"},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ],
            max_tokens=256,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Grok API error: {e}]"
