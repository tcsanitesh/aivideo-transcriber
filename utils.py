# utils.py

def allowed_file(filename):
    return filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks for embedding.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
