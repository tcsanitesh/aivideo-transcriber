# transcribe.py



import os
import tempfile
import whisper
from moviepy.editor import VideoFileClip
import yt_dlp
import shutil

def transcribe_video(video_path_or_url):
    """
    Extract audio from local video or YouTube URL and transcribe using OpenAI Whisper.
    Returns transcript as string.
    """
    # If input is a YouTube URL, download the video first
    if video_path_or_url.startswith('http'):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'video.mp4')
            ydl_opts = {
                'outtmpl': output_path,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'merge_output_format': 'mp4'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_path_or_url])
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
        # Extract audio
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)

        # Load Whisper model (use 'base' for speed, 'small' or 'medium' for better accuracy)
        model = whisper.load_model('base')
        result = model.transcribe(audio_path)
        transcript = result['text']
    except Exception as e:
        transcript = f"[Transcription failed: {e}]"
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        # Clean up downloaded YouTube video
        if video_path_or_url.startswith('http') and os.path.exists(video_path):
            os.remove(video_path)
    return transcript
