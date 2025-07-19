import streamlit as st
from transcribe import transcribe_video
from embed_store import store_embeddings, search_embeddings
from qa_engine import answer_query
from utils import allowed_file, generate_video_metadata
import os
import json

st.set_page_config(page_title="AI Video Transcriber & Knowledge Explorer", layout="wide")
st.title("🎥 AI Video Transcriber & Knowledge Explorer")

st.write("""
**Workflow:**
1. Upload a video or paste a YouTube link
2. Transcribe the video and generate comprehensive metadata
3. Generate embeddings & store in vector DB
4. Ask questions about the content
""")

# --- Step 1: Upload or Link Video ---
video_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi", "mkv"])
youtube_url = st.text_input("Or paste a YouTube URL", 
                           placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Add helpful tips
if youtube_url:
    st.info("💡 **YouTube URL Tips:**\n"
            "• Make sure the video is public and not age-restricted\n"
            "• Use the full URL from your browser's address bar\n"
            "• Short URLs (youtu.be) are also supported\n"
            "• Avoid playlists - use individual video URLs")

if 'transcript' not in st.session_state:
    st.session_state['transcript'] = None
if 'metadata' not in st.session_state:
    st.session_state['metadata'] = None
if 'context' not in st.session_state:
    st.session_state['context'] = None
if 'answer' not in st.session_state:
    st.session_state['answer'] = None

# --- Step 2: Transcription & Metadata Generation ---
if (video_file or youtube_url) and st.button('Transcribe Video'):
    if video_file:
        video_path = f"temp_{video_file.name}"
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        st.info("Processing uploaded video...")
    elif youtube_url:
        video_path = youtube_url
        st.info("Processing YouTube URL...")
    else:
        video_path = None
        
    if video_path:
        with st.spinner("Transcribing video... This may take a few minutes for longer videos."):
            transcript = transcribe_video(video_path)
            
        if isinstance(transcript, str) and transcript.startswith("[Error:"):
            st.error(transcript)
        else:
            st.session_state['transcript'] = transcript
            st.success("Transcription complete!")
            
            # Automatically generate metadata
            groq_api_key = st.text_input("Enter your Groq API Key for metadata generation", type="password")
            if groq_api_key:
                with st.spinner("Generating comprehensive metadata..."):
                    metadata = generate_video_metadata(transcript, groq_api_key)
                    st.session_state['metadata'] = metadata
                st.success("Metadata generation complete!")
            else:
                st.info("Enter your Groq API Key above to generate comprehensive metadata")
            
        # Clean up temporary file if it was created
        if video_file and os.path.exists(video_path):
            os.remove(video_path)

# --- Step 3: Display Metadata & Transcript ---
if st.session_state['transcript']:
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📊 Metadata Analysis", "📝 Transcript", "🔍 Q&A"])
    
    with tab1:
        if st.session_state['metadata']:
            metadata = st.session_state['metadata']
            
            if 'error' in metadata:
                st.error(f"Metadata generation failed: {metadata['error']}")
            else:
                # Main metadata display
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"## 🎯 {metadata.get('title', 'Content Analysis')}")
                    st.markdown(f"**{metadata.get('short_description', 'No description available')}**")
                    
                    st.markdown("### 📋 Detailed Description")
                    st.write(metadata.get('detailed_description', 'No detailed description available'))
                    
                    # Key highlights
                    st.markdown("### ⭐ Key Highlights")
                    highlights = metadata.get('key_highlights', [])
                    for i, highlight in enumerate(highlights, 1):
                        st.markdown(f"{i}. {highlight}")
                    
                    # Main takeaways
                    st.markdown("### 🎯 Main Takeaways")
                    takeaways = metadata.get('main_takeaways', [])
                    for i, takeaway in enumerate(takeaways, 1):
                        st.markdown(f"{i}. {takeaway}")
                
                with col2:
                    # Metadata cards
                    st.markdown("### 📊 Content Info")
                    
                    # Category and subcategory
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Category", metadata.get('category', 'Unknown'))
                    with col_b:
                        st.metric("Subcategory", metadata.get('subcategory', 'Unknown'))
                    
                    # Sentiment and difficulty
                    col_c, col_d = st.columns(2)
                    with col_c:
                        sentiment = metadata.get('sentiment', 'Unknown')
                        sentiment_color = {
                            'Positive': '🟢',
                            'Negative': '🔴', 
                            'Neutral': '🟡',
                            'Mixed': '🟠'
                        }.get(sentiment, '⚪')
                        st.metric("Sentiment", f"{sentiment_color} {sentiment}")
                    with col_d:
                        st.metric("Difficulty", metadata.get('difficulty_level', 'Unknown'))
                    
                    # Duration and audience
                    col_e, col_f = st.columns(2)
                    with col_e:
                        st.metric("Duration", metadata.get('estimated_duration', 'Unknown'))
                    with col_f:
                        st.metric("Audience", metadata.get('target_audience', 'General'))
                    
                    # Topics
                    st.markdown("### 🏷️ Topics")
                    topics = metadata.get('topics', [])
                    for topic in topics:
                        st.markdown(f"• {topic}")
                    
                    # Action items
                    st.markdown("### ✅ Action Items")
                    action_items = metadata.get('action_items', [])
                    for item in action_items:
                        st.markdown(f"• {item}")
                    
                    # Related concepts
                    st.markdown("### 🔗 Related Concepts")
                    related = metadata.get('related_concepts', [])
                    for concept in related:
                        st.markdown(f"• {concept}")
        else:
            st.info("No metadata available. Enter your Groq API Key and regenerate to get comprehensive analysis.")
    
    with tab2:
        st.subheader("📝 Full Transcript")
        st.text_area("Transcript", st.session_state['transcript'], height=400)
        
        # Download transcript
        st.download_button(
            "📥 Download Transcript", 
            st.session_state['transcript'], 
            file_name="transcript.txt",
            mime="text/plain"
        )

    with tab3:
        st.subheader("🔍 Ask Questions About the Content")
        
        # Embedding generation
        if st.button('Generate Embeddings & Store'):
            with st.spinner("Generating embeddings and storing in vector DB..."):
                store_embeddings(st.session_state['transcript'])
            st.success("Embeddings stored!")
        
        # Q&A interface
        user_query = st.text_input("Your question:", placeholder="Ask anything about the video content...")
        if st.button('Get Answer') and user_query:
            with st.spinner("Searching for relevant context..."):
                context = search_embeddings(user_query)
                st.session_state['context'] = context
            
            with st.spinner("Generating answer..."):
                answer = answer_query(user_query, context)
                st.session_state['answer'] = answer
            
            st.success("Answer ready!")
        
        # Display answer
        if st.session_state['answer']:
            st.markdown("### 💡 Answer")
            st.markdown(f"**{st.session_state['answer']}**")
            
            # Show context used
            with st.expander("🔍 Show context used"):
                st.text(st.session_state['context'])
        
        # Example questions
        st.markdown("### 💭 Example Questions")
        st.markdown("""
        Try asking questions like:
        - What are the main points discussed?
        - What is the speaker's opinion on [topic]?
        - What solutions are proposed?
        - What are the key takeaways?
        - What problems are mentioned?
        """)
