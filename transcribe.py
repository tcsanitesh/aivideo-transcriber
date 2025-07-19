# transcribe.py



import os
import tempfile
import whisper
from moviepy.video.io.VideoFileClip import VideoFileClip
import yt_dlp
import shutil
import re
import subprocess

def check_ffmpeg_available():
    """
    Check if ffmpeg is available in the system.
    """
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_valid_youtube_url(url):
    """
    Check if the URL is a valid YouTube URL.
    """
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    return False

def transcribe_video(video_path_or_url):
    """
    Extract audio from local video or YouTube URL and transcribe using OpenAI Whisper.
    Returns transcript as string.
    """
    # If input is a YouTube URL, download the video first
    if video_path_or_url.startswith('http'):
        # Validate YouTube URL first
        if not is_valid_youtube_url(video_path_or_url):
            return "[Error: Invalid YouTube URL. Please provide a valid YouTube video URL.]"
            
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'video.mp4')
            ydl_opts = {
                'outtmpl': output_path,
                'format': 'best[ext=mp4]/best',  # Simplified format selection
                'merge_output_format': 'mp4',
                'ignoreerrors': True,  # Continue on errors
                'no_warnings': True,   # Reduce noise
                'quiet': True,         # Quiet mode
                'extract_flat': False, # Extract full video
                'nocheckcertificate': True,  # Skip certificate verification
                'prefer_ffmpeg': True, # Prefer ffmpeg for merging
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # First, try to extract info to validate URL
                    info = ydl.extract_info(video_path_or_url, download=False)
                    if info is None:
                        return "[Error: Could not extract video info. Please check the URL and try again.]"
                    
                    # Download the video
                    ydl.download([video_path_or_url])
                    
                    # Check if file was actually downloaded
                    if not os.path.exists(output_path):
                        return "[Error: Video download failed. Please check the URL and try again.]"
                        
            except Exception as e:
                return f"[YouTube download error: {str(e)}. Please check the URL and try again.]"
            
            # Move the downloaded file to a temp file for processing
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_vid:
                shutil.copyfile(output_path, temp_vid.name)
                video_path = temp_vid.name
    else:
        video_path = video_path_or_url

    # Extract audio to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_temp:
        audio_path = audio_temp.name
    try:
        # Check if ffmpeg is available
        if not check_ffmpeg_available():
            return "[Error: ffmpeg is not available. This is required for video processing. Please contact support or try uploading an audio file instead.]"
        
        # Extract audio
        video = VideoFileClip(video_path)
        if video.audio is None:
            return "[Error: No audio track found in the video.]"
            
        video.audio.write_audiofile(audio_path, logger=None)

        # Load Whisper model (use 'base' for speed, 'small' or 'medium' for better accuracy)
        model = whisper.load_model('base')
        result = model.transcribe(audio_path)
        transcript = result['text']
        
        if isinstance(transcript, str) and not transcript.strip():
            return "[Warning: Transcription completed but no text was detected. The video might be silent or contain no speech.]"
            
    except Exception as e:
        if "ffmpeg" in str(e).lower():
            return "[Error: ffmpeg is not properly installed or configured. This is required for video processing.]"
        else:
            return f"[Transcription failed: {e}]"
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        # Clean up downloaded YouTube video
        if video_path_or_url.startswith('http') and os.path.exists(video_path):
            os.remove(video_path)
    return transcript
