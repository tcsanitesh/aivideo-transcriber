#!/usr/bin/env python3
"""
Test script to verify Supabase connection and database setup
"""

import os
from supabase import create_client

def test_supabase_connection():
    """Test basic Supabase connection."""
    try:
        # Supabase credentials
        supabase_url = "https://lrowromhpwebukywmtem.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxyb3dyb21ocHdlYnVreXdtdGVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NzE5ODUsImV4cCI6MjA2ODU0Nzk4NX0.Pd74n0CbooCvF1AHFtRGpzCuzQJ7TjydZPzna16fp0I"
        
        # Create client
        client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully!")
        
        # Test connection by checking if tables exist
        try:
            # Try to query content_files table
            result = client.table("content_files").select("count", count="exact").execute()
            print("✅ Database connection successful!")
            print(f"📊 Content files in database: {result.count}")
            
            # Try to query metadata table
            result = client.table("metadata").select("count", count="exact").execute()
            print(f"📊 Metadata records in database: {result.count}")
            
            # Try to query embeddings table
            result = client.table("embeddings").select("count", count="exact").execute()
            print(f"📊 Embeddings records in database: {result.count}")
            
            # Try to query token_usage table
            result = client.table("token_usage").select("count", count="exact").execute()
            print(f"📊 Token usage records in database: {result.count}")
            
        except Exception as e:
            print(f"⚠️ Tables might not exist yet: {e}")
            print("💡 Please run the setup_database.sql script in your Supabase SQL Editor")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

def test_insert_sample_data():
    """Test inserting sample data."""
    try:
        # Supabase credentials
        supabase_url = "https://lrowromhpwebukywmtem.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxyb3dyb21ocHdlYnVreXdtdGVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NzE5ODUsImV4cCI6MjA2ODU0Nzk4NX0.Pd74n0CbooCvF1AHFtRGpzCuzQJ7TjydZPzna16fp0I"
        
        # Create client
        client = create_client(supabase_url, supabase_key)
        
        # Insert sample content file
        sample_data = {
            "filename": "test_sample.mp4",
            "file_type": "video",
            "transcript": "This is a test transcript for verifying the database connection.",
            "processing_status": "completed"
        }
        
        result = client.table("content_files").insert(sample_data).execute()
        
        if result.data:
            print("✅ Sample data inserted successfully!")
            print(f"📄 Inserted file ID: {result.data[0]['id']}")
            
            # Clean up - delete the test record
            file_id = result.data[0]['id']
            client.table("content_files").delete().eq("id", file_id).execute()
            print("🧹 Test data cleaned up")
            
            return True
        else:
            print("❌ Failed to insert sample data")
            return False
            
    except Exception as e:
        print(f"❌ Failed to insert sample data: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Supabase Connection...")
    print("=" * 50)
    
    # Test connection
    if test_supabase_connection():
        print("\n✅ Connection test passed!")
        
        # Test data insertion
        print("\n🔍 Testing data insertion...")
        if test_insert_sample_data():
            print("✅ Data insertion test passed!")
            print("\n🎉 All tests passed! Your Supabase setup is working correctly.")
        else:
            print("❌ Data insertion test failed!")
    else:
        print("❌ Connection test failed!")
        print("\n💡 Please check your Supabase credentials and database setup.")
