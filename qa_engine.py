# qa_engine.py

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def answer_query(query, context, groq_api_key=None):
    """
    Enhanced Q&A using Groq API with better response handling.
    Returns helpful answer even when context doesn't match exactly.
    """
    if groq_api_key is None:
        groq_api_key = os.getenv("GROK_API_KEY")
    if not groq_api_key:
        return "[Error: GROK_API_KEY not set]"
    
    try:
        client = Groq(api_key=groq_api_key)
        
        # Enhanced system prompt for better responses
        system_prompt = """You are a knowledgeable and helpful AI assistant. Your role is to:

1. **Primary**: Answer questions based on the provided context when possible
2. **Secondary**: If the exact answer isn't in the context, provide relevant general knowledge or insights
3. **Always**: Be helpful, informative, and educational

Guidelines:
- If the context contains relevant information, use it as your primary source
- If the context doesn't contain the specific answer, acknowledge this but provide helpful related information
- For technical questions, explain concepts clearly
- For opinion-based questions, provide balanced perspectives
- Always be honest about what you know vs. what you're inferring
- Keep responses concise but informative (2-3 sentences minimum)

Never just say "I don't know" - instead, provide context, related information, or explain why the question might be challenging to answer."""
        
        user_prompt = f"""Context from the document/content:
{context}

User Question: {query}

Please provide a helpful and informative response. If the exact answer isn't in the context, provide relevant general knowledge or insights instead of saying "I don't know." """
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=512,  # Increased for more detailed responses
            temperature=0.3  # Slightly higher for more creative responses
        )
        
        content = response.choices[0].message.content
        if content is None:
            return "[Error: No response from Groq API]"
        
        return content.strip()
        
    except Exception as e:
        return f"[Groq API error: {e}]"

def answer_query_with_metadata(query, context, metadata=None, groq_api_key=None):
    """
    Enhanced Q&A that also uses metadata for better context and responses.
    """
    if groq_api_key is None:
        groq_api_key = os.getenv("GROK_API_KEY")
    if not groq_api_key:
        return "[Error: GROK_API_KEY not set]"
    
    try:
        client = Groq(api_key=groq_api_key)
        
        # Build enhanced context with metadata
        enhanced_context = f"Content: {context}\n"
        if metadata and isinstance(metadata, dict) and 'error' not in metadata:
            enhanced_context += f"""
Additional Context:
- Title: {metadata.get('title', 'N/A')}
- Category: {metadata.get('category', 'N/A')}
- Topics: {', '.join(metadata.get('topics', []))}
- Key Highlights: {'; '.join(metadata.get('key_highlights', []))}
- Main Takeaways: {'; '.join(metadata.get('main_takeaways', []))}
- Sentiment: {metadata.get('sentiment', 'N/A')}
- Target Audience: {metadata.get('target_audience', 'N/A')}
"""
        
        system_prompt = """You are a knowledgeable AI assistant with access to both content and metadata. Your role is to:

1. **Primary**: Answer questions using the provided content and metadata
2. **Secondary**: Provide relevant insights even when exact answers aren't available
3. **Always**: Be helpful, informative, and educational

Use the metadata to provide better context and more informed responses. If the content doesn't contain the specific answer, use the metadata to provide related insights or general knowledge."""
        
        user_prompt = f"""Content and Metadata:
{enhanced_context}

User Question: {query}

Please provide a comprehensive and helpful response using both the content and metadata when available."""
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=512,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        if content is None:
            return "[Error: No response from Groq API]"
        
        return content.strip()
        
    except Exception as e:
        return f"[Groq API error: {e}]"
