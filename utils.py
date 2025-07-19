# utils.py

import os
from groq import Groq

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


def generate_video_metadata(transcript, groq_api_key=None):
    """
    Use Groq API to generate comprehensive video metadata from transcript.
    Returns a dictionary with title, description, highlights, takeaways, category, etc.
    """
    if groq_api_key is None:
        groq_api_key = os.getenv("GROK_API_KEY")
    if not groq_api_key:
        return {"error": "GROK_API_KEY not set"}
    
    prompt = f"""
    Based on the following transcript, provide comprehensive metadata in JSON format:

    TRANSCRIPT:
    {transcript}

    Please analyze and provide the following information in a structured JSON format:
    {{
        "title": "A compelling, SEO-friendly title (max 60 characters)",
        "short_description": "A concise summary in 1-2 sentences (max 150 characters)",
        "detailed_description": "A comprehensive description of the content (2-3 paragraphs)",
        "key_highlights": ["Highlight 1", "Highlight 2", "Highlight 3", "Highlight 4", "Highlight 5"],
        "main_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
        "category": "Primary category (e.g., Technology, Education, Entertainment, Business, etc.)",
        "subcategory": "More specific subcategory",
        "topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4"],
        "sentiment": "Overall sentiment (Positive, Negative, Neutral, Mixed)",
        "target_audience": "Who would benefit from this content",
        "estimated_duration": "Estimated duration in minutes based on content length",
        "difficulty_level": "Beginner, Intermediate, or Advanced",
        "action_items": ["Action item 1", "Action item 2", "Action item 3"],
        "related_concepts": ["Related concept 1", "Related concept 2", "Related concept 3"]
    }}

    Focus on accuracy and provide actionable insights. If the transcript is unclear or too short, indicate that in the response.
    """
    
    try:
        client = Groq(api_key=groq_api_key)
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are an expert content analyst. Provide accurate, structured metadata in JSON format. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        if content is None:
            return {"error": "No content returned from Groq API"}
        
        # Try to extract JSON from the response
        import json
        try:
            # Find JSON in the response (sometimes it's wrapped in markdown)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content.strip()
            
            metadata = json.loads(json_str)
            return metadata
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return a structured response
            return {
                "title": "Content Analysis",
                "short_description": content[:150] + "..." if len(content) > 150 else content,
                "detailed_description": content,
                "key_highlights": ["Content analyzed successfully"],
                "main_takeaways": ["See detailed description"],
                "category": "General",
                "subcategory": "Analysis",
                "topics": ["Content Analysis"],
                "sentiment": "Neutral",
                "target_audience": "General",
                "estimated_duration": "Unknown",
                "difficulty_level": "General",
                "action_items": ["Review the detailed description"],
                "related_concepts": ["Content Analysis"]
            }
            
    except Exception as e:
        return {"error": f"Groq API error: {e}"}
