try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    print("moviepy.editor imported successfully!")
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        print("moviepy.video.editor imported successfully!")
    except ImportError:
        print("moviepy is not installed or could not be imported.")
        print("moviepy.video.editor imported successfully!")
    except ImportError:
        print("moviepy is not installed or could not be imported.")