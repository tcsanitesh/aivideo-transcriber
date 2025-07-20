import streamlit as st
from transcribe import process_content
from embed_store import store_embeddings, search_embeddings
from qa_engine import answer_query, answer_query_with_metadata
from utils import allowed_file, generate_video_metadata
from supabase_storage import get_storage_manager
from supabase_auth import show_auth_ui
import os
import json
import time
import uuid
from groq import Groq

def initialize_session():
    """Initialize session state for user management."""
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid.uuid4())
    
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    
    if 'is_authenticated' not in st.session_state:
        st.session_state['is_authenticated'] = False

def show_login_section():
    """Show login/registration section."""
    st.markdown("## 🔐 User Authentication")
    
    # Simple authentication options
    auth_option = st.radio(
        "Choose authentication method:",
        ["Anonymous Session", "Email/Password", "Quick Login"]
    )
    
    if auth_option == "Anonymous Session":
        st.info("🔒 Using anonymous session - your data will be isolated to this browser session")
        st.session_state['user_id'] = f"anon_{st.session_state['session_id']}"
        st.session_state['is_authenticated'] = True
        st.success("✅ Anonymous session created!")
        return True
    
    elif auth_option == "Email/Password":
        st.warning("⚠️ Email/Password authentication requires Supabase Auth setup")
        st.info("For now, use 'Anonymous Session' or 'Quick Login'")
        return False
    
    elif auth_option == "Quick Login":
        # Simple username-based login for demo
        username = st.text_input("Enter a username:", placeholder="e.g., john_doe")
        
        if st.button("Login", type="primary"):
            if username and len(username) > 2:
                st.session_state['user_id'] = f"user_{username}_{int(time.time())}"
                st.session_state['is_authenticated'] = True
                st.success(f"✅ Logged in as {username}!")
                return True
            else:
                st.error("❌ Please enter a valid username (at least 3 characters)")
                return False
    
    return False

def validate_groq_api_key(api_key):
    """Validate Groq API key by making a test request."""
    try:
        client = Groq(api_key=api_key)
        # Make a simple test request
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        return True, "API key is valid!"
    except Exception as e:
        return False, f"Invalid API key: {str(e)}"

def show_notification(message, notification_type="success", duration=10):
    """Show a notification that disappears after specified duration."""
    notification_class = f"notification {notification_type}"
    st.markdown(f"""
    <div class="{notification_class}" id="notification">
        {message}
    </div>
    <script>
        setTimeout(function() {{
            var notification = document.getElementById('notification');
            if (notification) {{
                notification.style.animation = 'slideOut 0.5s ease-in forwards';
                setTimeout(function() {{
                    notification.remove();
                }}, 500);
            }}
        }}, {duration * 1000});
    </script>
    <style>
        @keyframes slideOut {{
            from {{
                transform: translateX(0);
                opacity: 1;
            }}
            to {{
                transform: translateX(100%);
                opacity: 0;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

# Initialize session
initialize_session()

# Page configuration
st.set_page_config(
    page_title="AI Content Analyzer & Knowledge Explorer", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .developer-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .info-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .warning-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        animation: slideIn 0.5s ease-out;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .notification.success {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    }
    .notification.error {
        background: linear-gradient(135deg, #dc3545 0%, #e74c3c 100%);
    }
    .notification.warning {
        background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
    }
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
        transform: scale(1.05);
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    .stFileUploader > div {
        border-radius: 10px;
        border: 2px dashed #667eea;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }
    .stFileUploader > div:hover {
        border-color: #764ba2;
        background: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎥 AI Content Analyzer & Knowledge Explorer</h1>
    <p>Transform your videos, audio, and documents into actionable insights with AI-powered analysis</p>
</div>
<div class="developer-info">
    <p>🚀 Developed by <strong>Anitesh Shaw</strong></p>
</div>
""", unsafe_allow_html=True)

# Authentication Check
if not st.session_state.get('is_authenticated', False):
    if show_auth_ui():
        st.rerun()
    else:
        st.stop()

# Show current user info
if st.session_state.get('user_id'):
    user_email = st.session_state.get('user_email', 'Unknown')
    user_display = user_email if '@' in user_email else st.session_state['user_id'].replace('anon_', 'Anonymous User ').replace('user_', 'User: ')
    st.info(f"👤 Logged in as: {user_display}")
    
    # Logout option
    if st.button("🚪 Logout"):
        st.session_state['is_authenticated'] = False
        st.session_state['user_id'] = None
        st.session_state['user_email'] = None
        st.rerun()

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = None
if 'metadata' not in st.session_state:
    st.session_state['metadata'] = None
if 'context' not in st.session_state:
    st.session_state['context'] = None
if 'answer' not in st.session_state:
    st.session_state['answer'] = None
if 'embeddings_generated' not in st.session_state:
    st.session_state['embeddings_generated'] = False
if 'processing_complete' not in st.session_state:
    st.session_state['processing_complete'] = False
if 'token_usage' not in st.session_state:
    st.session_state['token_usage'] = {'input_tokens': 0, 'output_tokens': 0, 'estimated_cost': 0}
if 'current_query' not in st.session_state:
    st.session_state['current_query'] = None
if 'qa_mode' not in st.session_state:
    st.session_state['qa_mode'] = None

# Step 1: Groq API Key Input
st.markdown("## 🔑 Step 1: API Configuration")

# Initialize session state for API validation
if 'api_validated' not in st.session_state:
    st.session_state['api_validated'] = False
if 'api_validation_message' not in st.session_state:
    st.session_state['api_validation_message'] = ""

groq_api_key = st.text_input(
    "Enter your Groq API Key", 
    type="password", 
    help="Required for content analysis and Q&A. Get your free API key from https://console.groq.com/",
    placeholder="gsk_...",
    key="api_key_input"
)

# API Key validation
if groq_api_key:
    if not groq_api_key.startswith("gsk_"):
        st.error("❌ Invalid API key format. Groq API keys start with 'gsk_'")
        st.session_state['api_validated'] = False
    else:
        # Validate API key
        if st.button("🔍 Validate API Key", type="secondary"):
            with st.spinner("🔍 Validating API key..."):
                is_valid, message = validate_groq_api_key(groq_api_key)
                st.session_state['api_validated'] = is_valid
                st.session_state['api_validation_message'] = message
                
                if is_valid:
                    show_notification("✅ API key validated successfully!", "success", 5)
                else:
                    show_notification("❌ API key validation failed!", "error", 5)
        
        # Show validation status
        if st.session_state['api_validation_message']:
            if st.session_state['api_validated']:
                st.success(f"✅ {st.session_state['api_validation_message']}")
            else:
                st.error(f"❌ {st.session_state['api_validation_message']}")
        
        # Show validation status indicator
        if st.session_state['api_validated']:
            st.markdown("""
            <div class="success-box">
                <h4>🔐 API Key Status: Valid</h4>
                <p>Your API key has been validated and is ready to use!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <h4>⚠️ API Key Status: Not Validated</h4>
                <p>Please validate your API key before proceeding to ensure it works correctly.</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Please enter your Groq API key to continue")
    st.session_state['api_validated'] = False

# Step 2: Content Upload
st.markdown("## 📁 Step 2: Upload Content")
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Upload File")
    video_file = st.file_uploader(
        "Choose a file", 
        type=["mp4", "mov", "avi", "mkv", "wav", "mp3", "m4a", "pdf", "doc", "docx", "txt", "ppt", "pptx", "xls", "xlsx"],
        help="Supported formats: Video, Audio, Documents (PDF, DOC, PPT, XLS, TXT)"
    )

with col2:
    st.markdown("### Or YouTube URL")
    youtube_url = st.text_input(
        "Paste YouTube URL", 
        placeholder="https://www.youtube.com/watch?v=...",
        help="Enter a valid YouTube video URL"
    )

# Processing button
if (video_file or youtube_url) and groq_api_key:
    # Check if API key is validated
    if not st.session_state.get('api_validated', False):
        st.error("❌ Please validate your API key before processing content.")
        st.info("💡 Click the 'Validate API Key' button above to ensure your key works correctly.")
    else:
        if st.button("🚀 Process Content", type="primary", use_container_width=True):
            # Reset states
            st.session_state['processing_complete'] = False
            st.session_state['embeddings_generated'] = False
            st.session_state['token_usage'] = {'input_tokens': 0, 'output_tokens': 0, 'estimated_cost': 0}
            
            # Initialize storage manager
            storage_manager = get_storage_manager()
            
            # Process content
            if video_file:
                video_path = f"temp_{video_file.name}"
                with open(video_path, "wb") as f:
                    f.write(video_file.read())
                st.info(f"📁 Processing uploaded file: {video_file.name}")
                filename = video_file.name
                file_size = video_file.size
                source_url = None
            elif youtube_url:
                video_path = youtube_url
                st.info("📺 Processing YouTube URL...")
                filename = f"youtube_{int(time.time())}.mp4"
                file_size = None
                source_url = youtube_url
            
            # Content processing
            with st.spinner("🔄 Extracting content..."):
                transcript = process_content(video_path)
                
            if isinstance(transcript, str) and transcript.startswith("[Error:"):
                st.error(transcript)
            else:
                st.session_state['transcript'] = transcript
                st.success("✅ Content extraction complete!")
                
                # Save transcript to Supabase
                with st.spinner("💾 Saving transcript to database..."):
                    file_type = filename.split('.')[-1] if '.' in filename else 'unknown'
                    # Ensure transcript is a string
                    transcript_str = str(transcript) if transcript is not None else ""
                    save_result = storage_manager.save_transcript(
                        filename=filename,
                        transcript=transcript_str,
                        file_type=file_type,
                        file_size=file_size,
                        source_url=source_url
                    )
                    
                    if save_result['success']:
                        file_id = save_result['file_id']
                        st.session_state['current_file_id'] = file_id
                        st.success("✅ Transcript saved to database!")
                    else:
                        st.error(f"❌ Failed to save transcript: {save_result.get('error', 'Unknown error')}")
                
                # Generate metadata
                with st.spinner("🧠 Generating comprehensive metadata..."):
                    metadata = generate_video_metadata(transcript, groq_api_key)
                    st.session_state['metadata'] = metadata
                    
                    # Update token usage if available
                    if metadata and 'token_usage' in metadata:
                        st.session_state['token_usage'] = metadata['token_usage']
                        
                st.success("✅ Metadata generation complete!")
                
                # Save metadata to Supabase
                if 'current_file_id' in st.session_state and metadata and 'error' not in metadata:
                    with st.spinner("💾 Saving metadata to database..."):
                        # Remove token_usage from metadata before saving
                        metadata_to_save = {k: v for k, v in metadata.items() if k != 'token_usage'}
                        save_metadata_result = storage_manager.save_metadata(
                            file_id=st.session_state['current_file_id'],
                            metadata=metadata_to_save
                        )
                        
                        if save_metadata_result['success']:
                            st.success("✅ Metadata saved to database!")
                        else:
                            st.warning(f"⚠️ Failed to save metadata: {save_metadata_result.get('error', 'Unknown error')}")
                
                # Generate embeddings automatically
                with st.spinner("🔍 Generating embeddings for Q&A..."):
                    store_embeddings(transcript)
                    st.session_state['embeddings_generated'] = True
                st.success("✅ Embeddings generated!")
                
                # Save embeddings to Supabase
                if 'current_file_id' in st.session_state:
                    with st.spinner("💾 Saving embeddings to database..."):
                        # Get embeddings from embed_store
                        from embed_store import embedding_index, chunks_store
                        if embedding_index is not None and chunks_store:
                            # Convert FAISS index to list for storage
                            embeddings_list = []
                            for i, chunk in enumerate(chunks_store):
                                # Get embedding for this chunk
                                from sentence_transformers import SentenceTransformer
                                model = SentenceTransformer('all-MiniLM-L6-v2')
                                embedding = model.encode([chunk])[0].tolist()
                                embeddings_list.append({
                                    'chunk': chunk,
                                    'embedding': embedding
                                })
                            
                            save_embeddings_result = storage_manager.save_embeddings(
                                file_id=st.session_state['current_file_id'],
                                embeddings=embeddings_list,
                                texts=chunks_store
                            )
                            
                            if save_embeddings_result['success']:
                                st.success("✅ Embeddings saved to database!")
                            else:
                                st.warning(f"⚠️ Failed to save embeddings: {save_embeddings_result.get('error', 'Unknown error')}")
                
                # Save token usage to Supabase
                if 'current_file_id' in st.session_state and st.session_state['token_usage']['input_tokens'] > 0:
                    storage_manager.save_token_usage(
                        file_id=st.session_state['current_file_id'],
                        operation="metadata_generation",
                        input_tokens=st.session_state['token_usage']['input_tokens'],
                        output_tokens=st.session_state['token_usage']['output_tokens'],
                        estimated_cost=st.session_state['token_usage']['estimated_cost']
                    )
                
                # Mark processing as complete
                st.session_state['processing_complete'] = True
                
                # Clean up temporary file
                if video_file and os.path.exists(video_path):
                    os.remove(video_path)
                
                st.success("🎉 All processing complete! Scroll down to view results.")

# Display results if processing is complete
if st.session_state['processing_complete'] and st.session_state['transcript']:
    st.markdown("## 📊 Analysis Results")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Metadata Analysis", "📝 Content", "🔍 Q&A", "🗂️ File Management"])
    
    with tab1:
        if st.session_state['metadata']:
            metadata = st.session_state['metadata']
            
            if 'error' in metadata:
                st.error(f"Metadata generation failed: {metadata['error']}")
            else:
                # Main metadata display with enhanced styling
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### 🎯 {metadata.get('title', 'Content Analysis')}")
                    st.markdown(f"**{metadata.get('short_description', 'No description available')}**")
                    
                    st.markdown("### 📋 Detailed Description")
                    st.write(metadata.get('detailed_description', 'No detailed description available'))
                    
                    # Key highlights
                    st.markdown("### ⭐ Key Highlights")
                    highlights = metadata.get('key_highlights', [])
                    for i, highlight in enumerate(highlights, 1):
                        st.markdown(f"**{i}.** {highlight}")
                    
                    # Main takeaways
                    st.markdown("### 🎯 Main Takeaways")
                    takeaways = metadata.get('main_takeaways', [])
                    for i, takeaway in enumerate(takeaways, 1):
                        st.markdown(f"**{i}.** {takeaway}")
                
                with col2:
                    # Metadata cards with enhanced styling
                    st.markdown("### 📊 Content Info")
                    
                    # Category and subcategory
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Category</h4>
                            <p>{metadata.get('category', 'Unknown')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Subcategory</h4>
                            <p>{metadata.get('subcategory', 'Unknown')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
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
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Sentiment</h4>
                            <p>{sentiment_color} {sentiment}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_d:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Difficulty</h4>
                            <p>{metadata.get('difficulty_level', 'Unknown')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Duration and audience
                    col_e, col_f = st.columns(2)
                    with col_e:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Duration</h4>
                            <p>{metadata.get('estimated_duration', 'Unknown')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_f:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Audience</h4>
                            <p>{metadata.get('target_audience', 'General')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
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
            st.info("No metadata available.")
    
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
        
        # Q&A interface using form to prevent tab jumping
        with st.form("qa_form", clear_on_submit=False):
            user_query = st.text_input("Your question:", placeholder="Ask anything about the content...")
            submit_button = st.form_submit_button('Get Answer', type="primary")
            
            if submit_button and user_query:
                # Store the query in session state to prevent form clearing
                st.session_state['current_query'] = user_query
                st.session_state['qa_mode'] = qa_mode
                
                # Process the Q&A
                if qa_mode == "Smart Search (Recommended)" and st.session_state['embeddings_generated']:
                    with st.spinner("🔍 Searching for relevant context..."):
                        context = search_embeddings(user_query)
                        st.session_state['context'] = context
                    
                    with st.spinner("🧠 Generating answer..."):
                        answer, qa_tokens = answer_query_with_metadata(user_query, context, st.session_state['metadata'], groq_api_key)
                        st.session_state['answer'] = answer
                        
                        # Update total token usage
                        if qa_tokens:
                            st.session_state['token_usage']['input_tokens'] += qa_tokens['input_tokens']
                            st.session_state['token_usage']['output_tokens'] += qa_tokens['output_tokens']
                            st.session_state['token_usage']['estimated_cost'] += qa_tokens['estimated_cost']
                else:
                    # Direct Analysis mode - use full content
                    with st.spinner("🧠 Analyzing full content..."):
                        full_content = st.session_state['transcript']
                        answer, qa_tokens = answer_query_with_metadata(user_query, full_content, st.session_state['metadata'], groq_api_key)
                        st.session_state['answer'] = answer
                        st.session_state['context'] = "(Using full content for analysis)"
                        
                        # Update total token usage
                        if qa_tokens:
                            st.session_state['token_usage']['input_tokens'] += qa_tokens['input_tokens']
                            st.session_state['token_usage']['output_tokens'] += qa_tokens['output_tokens']
                            st.session_state['token_usage']['estimated_cost'] += qa_tokens['estimated_cost']
                
                show_notification("✅ Answer generated successfully!", "success", 5)
                st.success("✅ Answer ready!")
        
        # Display answer (outside the form to prevent clearing)
        if st.session_state.get('answer'):
            st.markdown("### 💡 Answer")
            st.markdown(f"**{st.session_state['answer']}**")
            
            # Show context used
            with st.expander("🔍 Show context used"):
                st.text(st.session_state.get('context', 'No context available'))
            
            # Show the question that was asked
            if st.session_state.get('current_query'):
                st.markdown(f"**Question:** {st.session_state['current_query']}")
            
            # Clear answer button
            if st.button("🗑️ Clear Answer", type="secondary"):
                st.session_state['answer'] = None
                st.session_state['current_query'] = None
                st.session_state['context'] = None
                st.rerun()
        
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
    
    with tab4:
        st.subheader("🗂️ File Management")
        
        # Initialize storage manager
        storage_manager = get_storage_manager()
        
        # Search functionality
        st.markdown("### 🔍 Search Files")
        search_query = st.text_input("Search by filename or content:", placeholder="Enter search terms...")
        
        if search_query:
            search_results = storage_manager.search_files(search_query)
            if search_results:
                st.success(f"Found {len(search_results)} files matching '{search_query}'")
            else:
                st.info("No files found matching your search.")
        else:
            # Show all files
            all_files = storage_manager.get_all_files()
            if all_files:
                st.success(f"Found {len(all_files)} files in database")
            else:
                st.info("No files found in database.")
        
        # Display files
        files_to_display = search_results if search_query else all_files
        
        if files_to_display:
            st.markdown("### 📋 File List")
            
            for file_data in files_to_display:
                with st.expander(f"📄 {file_data['filename']} ({file_data['file_type']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**File ID:** {file_data['id']}")
                        st.markdown(f"**Type:** {file_data['file_type']}")
                        st.markdown(f"**Status:** {file_data['processing_status']}")
                        st.markdown(f"**Created:** {file_data['created_at'][:19]}")
                        
                        if file_data['file_size']:
                            st.markdown(f"**Size:** {file_data['file_size']:,} bytes")
                        
                        if file_data['source_url']:
                            st.markdown(f"**Source:** {file_data['source_url']}")
                        
                        # Show transcript preview
                        if file_data['transcript']:
                            transcript_preview = file_data['transcript'][:200] + "..." if len(file_data['transcript']) > 200 else file_data['transcript']
                            st.markdown(f"**Transcript Preview:** {transcript_preview}")
                    
                    with col2:
                        # Action buttons
                        if st.button(f"📥 Download", key=f"download_{file_data['id']}"):
                            st.download_button(
                                "📥 Download Transcript",
                                file_data['transcript'],
                                file_name=f"{file_data['filename']}_transcript.txt",
                                mime="text/plain"
                            )
                        
                        if st.button(f"🗑️ Delete", key=f"delete_{file_data['id']}"):
                            if storage_manager.delete_file(file_data['id']):
                                st.success("File deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete file")
                        
                        # Load file for analysis
                        if st.button(f"📊 Analyze", key=f"analyze_{file_data['id']}"):
                            # Load transcript into session state
                            st.session_state['transcript'] = file_data['transcript']
                            
                            # Load metadata
                            metadata = storage_manager.get_metadata(file_data['id'])
                            if metadata:
                                st.session_state['metadata'] = metadata
                            
                            # Load embeddings
                            embeddings_data = storage_manager.get_embeddings(file_data['id'])
                            if embeddings_data:
                                # Reconstruct FAISS index
                                from embed_store import store_embeddings
                                store_embeddings(file_data['transcript'])
                                st.session_state['embeddings_generated'] = True
                            
                            st.session_state['processing_complete'] = True
                            st.session_state['current_file_id'] = file_data['id']
                            
                            st.success("✅ File loaded for analysis! Switch to other tabs to view results.")
                            st.rerun()
        
        # Token usage summary
        st.markdown("### 💰 Token Usage Summary")
        usage_summary = storage_manager.get_token_usage_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Input Tokens", f"{usage_summary['total_input_tokens']:,}")
        with col2:
            st.metric("Total Output Tokens", f"{usage_summary['total_output_tokens']:,}")
        with col3:
            st.metric("Total Cost", f"${usage_summary['total_cost']:.4f}")
        with col4:
            st.metric("Operations", usage_summary['operations_count'])

# Cost estimation (placeholder - would need actual token counting)
if st.session_state['token_usage']['input_tokens'] > 0:
    st.markdown("## 💰 Cost Estimation")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Input Tokens", f"{st.session_state['token_usage']['input_tokens']:,}")
    with col2:
        st.metric("Output Tokens", f"{st.session_state['token_usage']['output_tokens']:,}")
    with col3:
        st.metric("Estimated Cost", f"${st.session_state['token_usage']['estimated_cost']:.4f}")
    
    st.info("💡 Cost estimates are approximate. Actual costs may vary based on Groq's pricing.")

# Footer with developer information
st.markdown("---")
st.markdown("""
<div class="developer-info">
    <p>🚀 <strong>AI Content Analyzer & Knowledge Explorer</strong></p>
    <p>Developed by <strong>Anitesh Shaw</strong></p>
    <p>🔗 <a href="https://linkedin.com/in/aniteshshaw" target="_blank" style="color: white;">LinkedIn Profile</a> | 🔗 <a href="https://github.com/tcsanitesh/aivideo-transcriber" target="_blank" style="color: white;">GitHub Repository</a></p>
</div>
""", unsafe_allow_html=True)
