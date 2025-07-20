"""
Supabase Storage Manager for AI Content Analyzer
Provides persistent storage for transcripts, metadata, and processing history
"""

import os
import json
import time
import pickle
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import streamlit as st

class SupabaseStorageManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client and storage manager."""
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client = create_client(supabase_url, supabase_key)
        self.current_user_id = None
        
        # Initialize database tables if they don't exist
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables (this will be done via Supabase dashboard)."""
        # Tables will be created manually in Supabase dashboard
        # This is just a placeholder for documentation
        pass
    
    def set_current_user(self, user_id: str):
        """Set the current user ID for data isolation."""
        self.current_user_id = user_id
    
    def get_current_user_id(self) -> Optional[str]:
        """Get current user ID from session state or return None for anonymous."""
        if self.current_user_id:
            return self.current_user_id
        
        # Try to get from Streamlit session state
        return st.session_state.get('user_id', None)
    
    def save_transcript(self, filename: str, transcript: str, file_type: str = "unknown", 
                       file_size: Optional[int] = None, source_url: Optional[str] = None) -> Dict:
        """Save transcript to Supabase database with user isolation."""
        try:
            user_id = self.get_current_user_id()
            
            # Create content record
            content_data = {
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "source_url": source_url,
                "transcript": transcript,
                "processing_status": "transcript_saved",
                "created_at": datetime.now().isoformat(),
                "user_id": user_id  # Add user_id for isolation
            }
            
            result = self.client.table("content_files").insert(content_data).execute()
            
            if result.data:
                file_id = result.data[0]["id"]
                st.success(f"✅ Transcript saved with ID: {file_id}")
                return {"success": True, "file_id": file_id, "data": result.data[0]}
            else:
                st.error("❌ Failed to save transcript")
                return {"success": False, "error": "No data returned"}
                
        except Exception as e:
            st.error(f"❌ Error saving transcript: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def save_metadata(self, file_id: int, metadata: Dict) -> Dict:
        """Save metadata to Supabase database."""
        try:
            metadata_data = {
                "file_id": file_id,
                "metadata": json.dumps(metadata),
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("metadata").insert(metadata_data).execute()
            
            if result.data:
                # Update content file status
                self.client.table("content_files").update({
                    "processing_status": "metadata_saved"
                }).eq("id", file_id).execute()
                
                st.success("✅ Metadata saved successfully")
                return {"success": True, "data": result.data[0]}
            else:
                st.error("❌ Failed to save metadata")
                return {"success": False, "error": "No data returned"}
                
        except Exception as e:
            st.error(f"❌ Error saving metadata: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def save_embeddings(self, file_id: int, embeddings: List, texts: List[str]) -> Dict:
        """Save embeddings to Supabase storage."""
        try:
            # Convert embeddings to base64 for storage
            embeddings_data = {
                "embeddings": embeddings,
                "texts": texts,
                "file_id": file_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store as JSON in database (for small embeddings)
            # For large embeddings, consider using Supabase Storage
            embeddings_json = json.dumps(embeddings_data, default=str)
            
            embedding_data = {
                "file_id": file_id,
                "embeddings_data": embeddings_json,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("embeddings").insert(embedding_data).execute()
            
            if result.data:
                # Update content file status
                self.client.table("content_files").update({
                    "processing_status": "embeddings_saved"
                }).eq("id", file_id).execute()
                
                st.success("✅ Embeddings saved successfully")
                return {"success": True, "data": result.data[0]}
            else:
                st.error("❌ Failed to save embeddings")
                return {"success": False, "error": "No data returned"}
                
        except Exception as e:
            st.error(f"❌ Error saving embeddings: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def save_token_usage(self, file_id: int, operation: str, input_tokens: int, 
                        output_tokens: int, estimated_cost: float) -> Dict:
        """Save token usage to database."""
        try:
            user_id = self.get_current_user_id()
            
            usage_data = {
                "file_id": file_id,
                "operation": operation,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "estimated_cost": estimated_cost,
                "created_at": datetime.now().isoformat(),
                "user_id": user_id  # Add user_id for isolation
            }
            
            result = self.client.table("token_usage").insert(usage_data).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "No data returned"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_files(self) -> List[Dict]:
        """Get all processed files from database for current user."""
        try:
            user_id = self.get_current_user_id()
            
            if user_id:
                # Get files for specific user
                result = self.client.table("content_files").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            else:
                # Get files for anonymous user (session-based)
                session_id = st.session_state.get('session_id', 'anonymous')
                result = self.client.table("content_files").select("*").eq("user_id", session_id).order("created_at", desc=True).execute()
            
            return result.data if result.data else []
        except Exception as e:
            st.error(f"❌ Error fetching files: {str(e)}")
            return []
    
    def get_file_details(self, file_id: int) -> Optional[Dict]:
        """Get detailed information about a specific file."""
        try:
            user_id = self.get_current_user_id()
            
            if user_id:
                result = self.client.table("content_files").select("*").eq("id", file_id).eq("user_id", user_id).execute()
            else:
                session_id = st.session_state.get('session_id', 'anonymous')
                result = self.client.table("content_files").select("*").eq("id", file_id).eq("user_id", session_id).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"❌ Error fetching file details: {str(e)}")
            return None
    
    def get_transcript(self, file_id: int) -> Optional[str]:
        """Get transcript for a specific file."""
        try:
            user_id = self.get_current_user_id()
            
            if user_id:
                result = self.client.table("content_files").select("transcript").eq("id", file_id).eq("user_id", user_id).execute()
            else:
                session_id = st.session_state.get('session_id', 'anonymous')
                result = self.client.table("content_files").select("transcript").eq("id", file_id).eq("user_id", session_id).execute()
            
            return result.data[0]["transcript"] if result.data else None
        except Exception as e:
            st.error(f"❌ Error fetching transcript: {str(e)}")
            return None
    
    def get_metadata(self, file_id: int) -> Optional[Dict]:
        """Get metadata for a specific file."""
        try:
            result = self.client.table("metadata").select("*").eq("file_id", file_id).execute()
            if result.data:
                return json.loads(result.data[0]["metadata"])
            return None
        except Exception as e:
            st.error(f"❌ Error fetching metadata: {str(e)}")
            return None
    
    def get_embeddings(self, file_id: int) -> Optional[Dict]:
        """Get embeddings for a specific file."""
        try:
            result = self.client.table("embeddings").select("*").eq("file_id", file_id).execute()
            if result.data:
                embeddings_data = json.loads(result.data[0]["embeddings_data"])
                return embeddings_data
            return None
        except Exception as e:
            st.error(f"❌ Error fetching embeddings: {str(e)}")
            return None
    
    def get_token_usage_summary(self, file_id: Optional[int] = None) -> Dict:
        """Get token usage summary for current user."""
        try:
            user_id = self.get_current_user_id()
            
            if file_id:
                if user_id:
                    result = self.client.table("token_usage").select("*").eq("file_id", file_id).eq("user_id", user_id).execute()
                else:
                    session_id = st.session_state.get('session_id', 'anonymous')
                    result = self.client.table("token_usage").select("*").eq("file_id", file_id).eq("user_id", session_id).execute()
            else:
                if user_id:
                    result = self.client.table("token_usage").select("*").eq("user_id", user_id).execute()
                else:
                    session_id = st.session_state.get('session_id', 'anonymous')
                    result = self.client.table("token_usage").select("*").eq("user_id", session_id).execute()
            
            if result.data:
                total_input = sum(item["input_tokens"] for item in result.data)
                total_output = sum(item["output_tokens"] for item in result.data)
                total_cost = sum(item["estimated_cost"] for item in result.data)
                
                return {
                    "total_input_tokens": total_input,
                    "total_output_tokens": total_output,
                    "total_cost": total_cost,
                    "operations_count": len(result.data)
                }
            return {"total_input_tokens": 0, "total_output_tokens": 0, "total_cost": 0, "operations_count": 0}
        except Exception as e:
            st.error(f"❌ Error fetching token usage: {str(e)}")
            return {"total_input_tokens": 0, "total_output_tokens": 0, "total_cost": 0, "operations_count": 0}
    
    def delete_file(self, file_id: int) -> bool:
        """Delete file and all associated data for current user."""
        try:
            user_id = self.get_current_user_id()
            
            # Verify user owns the file before deleting
            if user_id:
                file_check = self.client.table("content_files").select("id").eq("id", file_id).eq("user_id", user_id).execute()
            else:
                session_id = st.session_state.get('session_id', 'anonymous')
                file_check = self.client.table("content_files").select("id").eq("id", file_id).eq("user_id", session_id).execute()
            
            if not file_check.data:
                st.error("❌ File not found or access denied")
                return False
            
            # Delete related records first
            self.client.table("token_usage").delete().eq("file_id", file_id).execute()
            self.client.table("embeddings").delete().eq("file_id", file_id).execute()
            self.client.table("metadata").delete().eq("file_id", file_id).execute()
            
            # Delete main file record
            self.client.table("content_files").delete().eq("id", file_id).execute()
            
            st.success("✅ File deleted successfully")
            return True
        except Exception as e:
            st.error(f"❌ Error deleting file: {str(e)}")
            return False
    
    def search_files(self, query: str) -> List[Dict]:
        """Search files by filename or content for current user."""
        try:
            user_id = self.get_current_user_id()
            
            if user_id:
                # Search in filename for specific user
                filename_results = self.client.table("content_files").select("*").eq("user_id", user_id).ilike("filename", f"%{query}%").execute()
                
                # Search in transcript content for specific user
                content_results = self.client.table("content_files").select("*").eq("user_id", user_id).ilike("transcript", f"%{query}%").execute()
            else:
                session_id = st.session_state.get('session_id', 'anonymous')
                # Search in filename for anonymous user
                filename_results = self.client.table("content_files").select("*").eq("user_id", session_id).ilike("filename", f"%{query}%").execute()
                
                # Search in transcript content for anonymous user
                content_results = self.client.table("content_files").select("*").eq("user_id", session_id).ilike("transcript", f"%{query}%").execute()
            
            # Combine and deduplicate results
            all_results = []
            seen_ids = set()
            
            for result in filename_results.data + content_results.data:
                if result["id"] not in seen_ids:
                    all_results.append(result)
                    seen_ids.add(result["id"])
            
            return all_results
        except Exception as e:
            st.error(f"❌ Error searching files: {str(e)}")
            return []

# Global storage manager instance
storage_manager = None

def get_storage_manager() -> SupabaseStorageManager:
    """Get or create global storage manager instance."""
    global storage_manager
    if storage_manager is None:
        # Get Supabase credentials from environment or Streamlit secrets
        supabase_url = os.getenv("SUPABASE_URL", "https://lrowromhpwebukywmtem.supabase.co")
        supabase_key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxyb3dyb21ocHdlYnVreXdtdGVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NzE5ODUsImV4cCI6MjA2ODU0Nzk4NX0.Pd74n0CbooCvF1AHFtRGpzCuzQJ7TjydZPzna16fp0I")
        
        storage_manager = SupabaseStorageManager(supabase_url, supabase_key)
    return storage_manager

def cleanup_storage():
    """Clean up storage manager."""
    global storage_manager
    storage_manager = None
