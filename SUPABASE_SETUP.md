# 🚀 Supabase Setup Guide for AI Content Analyzer

## 📋 Overview

This guide will help you set up Supabase for persistent storage of your AI Content Analyzer application. Supabase provides a PostgreSQL database with real-time capabilities and file storage.

## 🛠️ Setup Steps

### 1. Database Setup

1. **Go to your Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Sign in to your account
   - Select your project: `lrowromhpwebukywmtem`

2. **Open SQL Editor**
   - In the left sidebar, click on "SQL Editor"
   - Click "New Query"

3. **Run the Database Setup Script**
   - Copy the contents of `setup_database.sql`
   - Paste it into the SQL Editor
   - Click "Run" to execute the script

4. **Verify Tables Created**
   - Go to "Table Editor" in the left sidebar
   - You should see these tables:
     - `content_files`
     - `metadata`
     - `embeddings`
     - `token_usage`

### 2. Test Connection

Run the test script to verify everything is working:

```bash
python test_supabase.py
```

You should see:
```
✅ Supabase client created successfully!
✅ Database connection successful!
📊 Content files in database: 0
📊 Metadata records in database: 0
📊 Embeddings records in database: 0
📊 Token usage records in database: 0
✅ Sample data inserted successfully!
🎉 All tests passed!
```

### 3. Environment Variables (Optional)

For production deployment, you can set environment variables:

```bash
export SUPABASE_URL="https://lrowromhpwebukywmtem.supabase.co"
export SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxyb3dyb21ocHdlYnVreXdtdGVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NzE5ODUsImV4cCI6MjA2ODU0Nzk4NX0.Pd74n0CbooCvF1AHFtRGpzCuzQJ7TjydZPzna16fp0I"
```

## 📊 Database Schema

### content_files
- `id`: Primary key
- `filename`: Name of the uploaded file
- `file_type`: Type of file (video, audio, document)
- `file_size`: Size in bytes
- `source_url`: URL if from YouTube
- `transcript`: Extracted text content
- `processing_status`: Current processing status
- `created_at`: Timestamp
- `updated_at`: Last update timestamp

### metadata
- `id`: Primary key
- `file_id`: Foreign key to content_files
- `metadata`: JSON object with analysis results
- `created_at`: Timestamp

### embeddings
- `id`: Primary key
- `file_id`: Foreign key to content_files
- `embeddings_data`: JSON with embeddings and text chunks
- `created_at`: Timestamp

### token_usage
- `id`: Primary key
- `file_id`: Foreign key to content_files
- `operation`: Type of operation
- `input_tokens`: Number of input tokens
- `output_tokens`: Number of output tokens
- `estimated_cost`: Estimated cost in USD
- `created_at`: Timestamp

## 🔧 Features

### ✅ What's Working
- **Persistent Storage**: All data is saved to Supabase
- **File Management**: View, search, and manage uploaded files
- **Metadata Storage**: Analysis results are preserved
- **Embeddings Storage**: Vector embeddings for Q&A
- **Token Tracking**: Monitor API usage and costs
- **Search Functionality**: Search files by name or content

### 🚀 Deployment Ready
- **Streamlit Cloud Compatible**: Works perfectly with Streamlit Cloud
- **Multi-User Support**: Can handle multiple users
- **Scalable**: Can grow with your needs
- **Free Tier**: Generous free limits

## 🎯 Usage

1. **Upload/Process Content**: Files are automatically saved to database
2. **View Files**: Go to "File Management" tab to see all processed files
3. **Search Files**: Use the search function to find specific content
4. **Load for Analysis**: Click "Analyze" to reload any file for Q&A
5. **Download Transcripts**: Download any transcript as text file
6. **Monitor Usage**: Track token usage and costs

## 🔒 Security

- **Row Level Security (RLS)**: Enabled on all tables
- **Anonymous Access**: Configured for demo purposes
- **Production Ready**: Can be enhanced with authentication

## 💰 Cost

- **Free Tier**: 500MB database, 1GB file storage
- **More than sufficient** for capstone project
- **No cost** during development and submission

## 🆘 Troubleshooting

### Connection Issues
- Verify Supabase URL and API key
- Check if tables exist in Table Editor
- Run `python test_supabase.py` to diagnose

### Data Not Saving
- Check browser console for errors
- Verify RLS policies are correct
- Ensure API key has proper permissions

### Performance Issues
- Check database size in Supabase dashboard
- Monitor query performance
- Consider indexing for large datasets

## 📞 Support

If you encounter issues:
1. Check the test script output
2. Verify database setup
3. Check Supabase dashboard for errors
4. Review the application logs

---

**Happy Coding! 🎉**
