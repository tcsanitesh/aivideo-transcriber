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
- **Whisper API** (for audio-to-text transcription)
- **Groq API** (for LLM-based summarization & Q&A)
- **FAISS** (Vector DB for embedding search)
- **SentenceTransformers** (for creating embeddings)
- **Streamlit** (UI)
- **Supabase** (PostgreSQL database for persistent storage)
- **LangChain** (for chaining steps and document retrieval)

---

## 🧱 Features

- Upload or link a video (YouTube or local)
- Transcribe the video to text
- Extract key topics and auto-summarize
- Ask natural language questions based on the video transcript
- Store vectorized chunks of the transcript in vector DB
- Use semantic search + LLM response (via Groq API)
- **Persistent storage** with Supabase PostgreSQL database
- **File management** with search and download capabilities
- **Token usage tracking** and cost estimation
- **Production-ready** deployment on Streamlit Cloud

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
├── embed_store.py           # Embedding generation & FAISS storage
├── qa_engine.py             # Query + vector search + Groq LLM response
├── supabase_storage.py      # Supabase database integration
├── utils.py                 # Helper functions
├── setup_database.sql       # Database schema setup
├── test_supabase.py         # Supabase connection test
├── requirements.txt
└── README.md

---

## 🚀 Setup Instructions

### 1. **Install Dependencies**
```bash
git clone <your-repo-url>
cd aivideo-transcriber
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. **Set Up Supabase Database**
1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `lrowromhpwebukywmtem`
3. Go to "SQL Editor" → "New Query"
4. Copy and paste the contents of `setup_database.sql`
5. Click "Run" to create the tables

### 3. **Test Connection**
```bash
python test_supabase.py
```

### 4. **Run Application**
```bash
streamlit run app.py
```

---

## 🔑 API Keys

- **Groq API Key**: Required for metadata generation and Q&A
- **Supabase**: Already configured with your project credentials
- Copy `.env.example` to `.env` and add your Groq API key.

## 🗂️ Database Setup

The application uses Supabase for persistent storage:
- **URL**: https://lrowromhpwebukywmtem.supabase.co
- **Tables**: content_files, metadata, embeddings, token_usage
- **Setup**: Run `setup_database.sql` in Supabase SQL Editor

---

## 📄 License

MIT
