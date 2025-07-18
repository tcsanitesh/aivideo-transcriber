aivideo-transcriber/

# 🎥 AI Video Transcriber & Knowledge Explorer

## 🔍 Overview

This is a capstone project built for an AI Bootcamp. It’s an end-to-end application that:

- Extracts transcript from video (via audio)
- Generates embeddings from transcript
- Stores them in a vector database (e.g., FAISS or Chroma)
- Uses a Grok API call to generate responses for user queries
- Enables users to ask questions based on the transcript and receive contextual, accurate answers

---

## 💡 Core Technologies

- **Python** (Backend processing)
- **Whisper API / Vosk / AssemblyAI** (for audio-to-text; free/local options available)
- **Grok API** (for LLM-based summarization & Q&A)
- **FAISS or ChromaDB** (Vector DB for embedding search)
- **SentenceTransformers / OpenAI Embedding or HuggingFace model** (for creating embeddings)
- **Streamlit or Gradio** (UI)
- **LangChain** (for chaining steps and document retrieval)

---

## 🧱 Features

- Upload or link a video (YouTube or local)
- Transcribe the video to text
- Extract key topics and auto-summarize
- Ask natural language questions based on the video transcript
- Store vectorized chunks of the transcript in vector DB
- Use semantic search + LLM response (via Grok API)
- Shareable interface (public URL via Streamlit/Gradio)

---

## 🛠️ How It Works

1. **Transcription**
    - Audio is extracted from video
    - Speech-to-text is done via Whisper or Vosk (offline/local option available)

2. **Embedding + Vector DB**
    - Transcripts are chunked (e.g., 500 characters)
    - Embeddings are generated using HuggingFace or sentence-transformers
    - FAISS or Chroma is used to index & search

3. **QnA Engine**
    - User enters a query
    - Matching transcript chunks are retrieved using vector similarity
    - Retrieved context is sent to Grok API with user query
    - Final answer is returned and displayed

4. **Frontend (Gradio/Streamlit)**
    - Upload or link video
    - View full transcript and summary
    - Ask questions & get answers
    - Download transcript or share link


    aivideo-transcriber/
├── app.py                   # Main Streamlit app
├── transcribe.py            # Audio extraction and transcription logic
├── embed_store.py           # Embedding generation & FAISS/ChromaDB storage
├── qa_engine.py             # Query + vector search + Grok LLM response
├── utils.py                 # Helper functions
├── requirements.txt
└── README.md

---

## 🚀 Setup Instructions

```bash
git clone <your-repo-url>
cd aivideo-transcriber
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔑 API Keys

- Copy `.env.example` to `.env` and add your keys.

---

## 📄 License

MIT
