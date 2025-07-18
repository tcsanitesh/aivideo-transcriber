import streamlit as st
from transcribe import transcribe_video
from embed_store import store_embeddings, search_embeddings
from qa_engine import answer_query
from utils import allowed_file, generate_video_metadata
import os

st.set_page_config(page_title="AI Video Transcriber & Knowledge Explorer", layout="wide")
st.title("🎥 AI Video Transcriber & Knowledge Explorer")

st.write("""
**Workflow:**
1. Upload a video or paste a YouTube link
2. Transcribe the video
3. Generate embeddings & store in vector DB
4. Ask questions about the content
""")

# --- Step 1: Upload or Link Video ---
video_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi", "mkv"])
youtube_url = st.text_input("Or paste a YouTube URL")

if 'transcript' not in st.session_state:
    st.session_state['transcript'] = None
if 'context' not in st.session_state:
    st.session_state['context'] = None
if 'answer' not in st.session_state:
    st.session_state['answer'] = None

# --- Step 2: Transcription ---
if (video_file or youtube_url) and st.button('Transcribe Video'):
    if video_file:
        video_path = f"temp_{video_file.name}"
        with open(video_path, "wb") as f:
            f.write(video_file.read())
    elif youtube_url:
        video_path = youtube_url  # Placeholder: treat as path for now
    else:
        video_path = None
    st.info("Transcribing... (this is a placeholder)")
    transcript = transcribe_video(video_path)
    st.session_state['transcript'] = transcript
    st.success("Transcription complete!")

# --- Step 3: Embedding & Vector DB ---
if st.session_state['transcript']:
    st.subheader("Transcript")
    st.text_area("Transcript", st.session_state['transcript'], height=200)
    if st.button('Generate Embeddings & Store'):
        st.info("Generating embeddings and storing in vector DB... (placeholder)")
        store_embeddings(st.session_state['transcript'])
        st.success("Embeddings stored!")

# --- Step 4: QnA ---
    st.subheader("Ask a Question about the Video")
    user_query = st.text_input("Your question:")
    if st.button('Get Answer') and user_query:
        st.info("Searching for relevant context... (placeholder)")
        context = search_embeddings(user_query)
        st.session_state['context'] = context
        st.info("Querying LLM... (placeholder)")
        answer = answer_query(user_query, context)
        st.session_state['answer'] = answer
        st.success("Answer ready!")
    if st.session_state['answer']:
        st.markdown(f"**Answer:** {st.session_state['answer']}")
        st.markdown(f"<details><summary>Show context</summary><pre>{st.session_state['context']}</pre></details>", unsafe_allow_html=True)

# --- Step 5: Download/Share ---
    st.download_button("Download Transcript", st.session_state['transcript'], file_name="transcript.txt")

# After transcript is generated and available in st.session_state['transcript']
groq_api_key = st.text_input("Enter your Groq API Key")  # or use from .env

if st.button("Generate Metadata with Groq") and st.session_state['transcript']:
    title, description, keywords, category = generate_video_metadata(
        st.session_state['transcript'], groq_api_key
    )
    st.markdown(f"**Title:** {title}")
    st.markdown(f"**Description:** {description}")
    st.markdown(f"**Keywords:** {keywords}")
    st.markdown(f"**Category:** {category}")
