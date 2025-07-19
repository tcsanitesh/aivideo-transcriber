# embed_store.py


import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from utils import chunk_text

# In-memory store for demo (replace with persistent DB for production)
embedding_index = None
chunks_store = []

def store_embeddings(transcript):
    """
    Chunk transcript, generate embeddings, and store in FAISS index.
    """
    global embedding_index, chunks_store
    chunks = chunk_text(transcript)
    if not chunks:
        raise ValueError("No chunks to embed from transcript.")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)
    embeddings = np.asarray(embeddings, dtype=np.float32)
    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)
    if embeddings.shape[0] == 0:
        raise ValueError("No embeddings to add to FAISS index.")
    dim = embeddings.shape[1]
    embedding_index = faiss.IndexFlatL2(dim)
    embedding_index.add(embeddings)  # type: ignore
    chunks_store = chunks

def search_embeddings(query, top_k=5):
    """
    Search FAISS index for relevant transcript chunks.
    Returns concatenated context string with improved fallback.
    """
    global embedding_index, chunks_store
    if embedding_index is None or not chunks_store:
        return "(No embeddings found - please generate embeddings first)"
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_emb = model.encode([query])
    query_emb = np.asarray(query_emb, dtype=np.float32)
    if query_emb.ndim == 1:
        query_emb = query_emb.reshape(1, -1)
    if query_emb.shape[0] == 0:
        return "(No embeddings found)"
    
    D, I = embedding_index.search(query_emb, top_k)  # type: ignore
    results = [chunks_store[i] for i in I[0] if i < len(chunks_store)]
    
    # If no relevant context, return a sample of the content
    if not results or all(r.strip() == '' for r in results):
        # Return first few chunks as general context
        sample_size = min(3, len(chunks_store))
        if sample_size > 0:
            return f"(No specific matches found. Here's a sample of the content: {' '.join(chunks_store[:sample_size])})"
        else:
            return "(No content available for analysis)"
    
    return '\n---\n'.join(results)

# def search_embeddings(query):
#     """
#     Search vector DB for relevant transcript chunks.
#     Returns context string.
#     """
#     # TODO: Implement semantic search
#     return "(Relevant context placeholder)"
