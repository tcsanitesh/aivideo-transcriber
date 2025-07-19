import streamlit as st
from transcribe import process_content
from embed_store import store_embeddings, search_embeddings
from qa_engine import answer_query, answer_query_with_metadata
from utils import allowed_file, generate_video_metadata
import os
import json

st.set_page_config(page_title="AI Content Analyzer & Knowledge Explorer", layout="wide")
st.title("🎥 AI Content Analyzer & Knowledge Explorer")

st.write("""
**Workflow:**
1. Upload a video/audio/document or paste a YouTube link
2. Extract text content and generate comprehensive metadata
3. Generate embeddings & store in vector DB
4. Ask questions about the content
""")

# --- Step 1: Upload or Link Content ---
video_file = st.file_uploader("Upload Video/Audio/Document", type=["mp4", "mov", "avi", "mkv", "wav", "mp3", "m4a", "pdf", "doc", "docx", "txt", "ppt", "pptx", "xls", "xlsx"])
youtube_url = st.text_input("Or paste a YouTube URL", 
                           placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Add helpful tips
if youtube_url:
    st.info("💡 **YouTube URL Tips:**\n"
            "• Make sure the video is public and not age-restricted\n"
            "• Use the full URL from your browser's address bar\n"
            "• Short URLs (youtu.be) are also supported\n"
            "• Avoid playlists - use individual video URLs")

# Groq API Key input (moved outside transcription flow)
groq_api_key = st.text_input("Enter your Groq API Key for metadata generation", type="password", 
                            help="Required for generating comprehensive metadata analysis")

if 'transcript' not in st.session_state:
    st.session_state['transcript'] = None
if 'metadata' not in st.session_state:
    st.session_state['metadata'] = None
if 'context' not in st.session_state:
    st.session_state['context'] = None
if 'answer' not in st.session_state:
    st.session_state['answer'] = None

# --- Step 2: Content Processing & Metadata Generation ---
if (video_file or youtube_url) and st.button('Process Content'):
    if video_file:
        video_path = f"temp_{video_file.name}"
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        st.info("Processing uploaded file...")
    elif youtube_url:
        video_path = youtube_url
        st.info("Processing YouTube URL...")
    else:
        video_path = None
        
    if video_path:
        with st.spinner("Processing content... This may take a few minutes for longer files."):
            transcript = process_content(video_path)
            
        if isinstance(transcript, str) and transcript.startswith("[Error:"):
            st.error(transcript)
        else:
            st.session_state['transcript'] = transcript
            st.success("Content processing complete!")
            
            # Generate metadata if Groq API key is provided
            if groq_api_key:
                with st.spinner("Generating comprehensive metadata..."):
                    metadata = generate_video_metadata(transcript, groq_api_key)
                    st.session_state['metadata'] = metadata
                st.success("Metadata generation complete!")
            else:
                st.warning("Enter your Groq API Key above to generate comprehensive metadata")
            
        # Clean up temporary file if it was created
        if video_file and os.path.exists(video_path):
            os.remove(video_path)

# --- Step 3: Display Metadata & Transcript ---
if st.session_state['transcript']:
    # Manual metadata generation button
    if not st.session_state['metadata'] and groq_api_key:
        if st.button('Generate Metadata Now'):
            with st.spinner("Generating comprehensive metadata..."):
                metadata = generate_video_metadata(st.session_state['transcript'], groq_api_key)
                st.session_state['metadata'] = metadata
            st.success("Metadata generation complete!")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📊 Metadata Analysis", "📝 Content", "🔍 Q&A"])
    
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
            st.info("No metadata available. Enter your Groq API Key and click 'Generate Metadata Now' to get comprehensive analysis.")
    
    with tab2:
        st.subheader("📝 Extracted Content")
        st.text_area("Content", st.session_state['transcript'], height=400)
        
        # Download content
        st.download_button(
            "📥 Download Content", 
            st.session_state['transcript'], 
            file_name="extracted_content.txt",
            mime="text/plain"
        )

    with tab3:
        st.subheader("🔍 Ask Questions About the Content")
        
        # Q&A Mode Selection
        qa_mode = st.radio(
            "Choose Q&A Mode:",
            ["Smart Search (Recommended)", "Direct Analysis"],
            help="Smart Search uses embeddings for precise answers. Direct Analysis uses the full content for comprehensive responses."
        )
        
        # Embedding generation (only for Smart Search mode)
        if qa_mode == "Smart Search (Recommended)":
            if st.button('Generate Embeddings & Store'):
                with st.spinner("Generating embeddings and storing in vector DB..."):
                    store_embeddings(st.session_state['transcript'])
                st.success("Embeddings stored!")
        
        # Q&A interface
        user_query = st.text_input("Your question:", placeholder="Ask anything about the content...")
        if st.button('Get Answer') and user_query:
            if qa_mode == "Smart Search (Recommended)":
                with st.spinner("Searching for relevant context..."):
                    context = search_embeddings(user_query)
                    st.session_state['context'] = context
                
                with st.spinner("Generating answer..."):
                    answer = answer_query_with_metadata(user_query, context, st.session_state['metadata'], groq_api_key)
                    st.session_state['answer'] = answer
            else:
                # Direct Analysis mode - use full content
                with st.spinner("Analyzing full content..."):
                    full_content = st.session_state['transcript']
                    answer = answer_query_with_metadata(user_query, full_content, st.session_state['metadata'], groq_api_key)
                    st.session_state['answer'] = answer
                    st.session_state['context'] = "(Using full content for analysis)"
            
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
        - Can you explain [specific concept]?
        - What is the overall sentiment?
        - Who is the target audience?
        """)
        
        # Tips for better Q&A
        st.markdown("### 💡 Tips for Better Answers")
        st.markdown("""
        - **Be specific**: Instead of "What is this about?", try "What are the main benefits discussed?"
        - **Use keywords**: Include key terms from the content in your questions
        - **Try different modes**: If Smart Search doesn't work, try Direct Analysis
        - **Ask follow-up questions**: Build on previous answers for deeper insights
        """)
