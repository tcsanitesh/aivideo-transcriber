-- Database setup script for AI Content Analyzer
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Content files table
CREATE TABLE IF NOT EXISTS content_files (
    id BIGSERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    source_url TEXT,
    transcript TEXT,
    processing_status VARCHAR(50) DEFAULT 'pending',
    user_id VARCHAR(255), -- For user isolation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Metadata table
CREATE TABLE IF NOT EXISTS metadata (
    id BIGSERIAL PRIMARY KEY,
    file_id BIGINT REFERENCES content_files(id) ON DELETE CASCADE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY,
    file_id BIGINT REFERENCES content_files(id) ON DELETE CASCADE,
    embeddings_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Token usage tracking table
CREATE TABLE IF NOT EXISTS token_usage (
    id BIGSERIAL PRIMARY KEY,
    file_id BIGINT REFERENCES content_files(id) ON DELETE CASCADE,
    operation VARCHAR(100),
    input_tokens INTEGER,
    output_tokens INTEGER,
    estimated_cost DECIMAL(10,6),
    user_id VARCHAR(255), -- For user isolation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_content_files_created_at ON content_files(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_files_filename ON content_files(filename);
CREATE INDEX IF NOT EXISTS idx_content_files_user_id ON content_files(user_id);
CREATE INDEX IF NOT EXISTS idx_metadata_file_id ON metadata(file_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_file_id ON embeddings(file_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_file_id ON token_usage(file_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_created_at ON token_usage(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_usage_user_id ON token_usage(user_id);

-- Create full-text search index on transcript
CREATE INDEX IF NOT EXISTS idx_content_files_transcript_fts ON content_files USING GIN (to_tsvector('english', transcript));

-- Enable Row Level Security (RLS)
ALTER TABLE content_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE token_usage ENABLE ROW LEVEL SECURITY;

-- Create policies for anonymous access (for demo purposes)
-- In production, you should implement proper authentication
CREATE POLICY "Allow anonymous read access" ON content_files FOR SELECT USING (true);
CREATE POLICY "Allow anonymous insert access" ON content_files FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous update access" ON content_files FOR UPDATE USING (true);
CREATE POLICY "Allow anonymous delete access" ON content_files FOR DELETE USING (true);

CREATE POLICY "Allow anonymous read access" ON metadata FOR SELECT USING (true);
CREATE POLICY "Allow anonymous insert access" ON metadata FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous update access" ON metadata FOR UPDATE USING (true);
CREATE POLICY "Allow anonymous delete access" ON metadata FOR DELETE USING (true);

CREATE POLICY "Allow anonymous read access" ON embeddings FOR SELECT USING (true);
CREATE POLICY "Allow anonymous insert access" ON embeddings FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous update access" ON embeddings FOR UPDATE USING (true);
CREATE POLICY "Allow anonymous delete access" ON embeddings FOR DELETE USING (true);

CREATE POLICY "Allow anonymous read access" ON token_usage FOR SELECT USING (true);
CREATE POLICY "Allow anonymous insert access" ON token_usage FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous update access" ON token_usage FOR UPDATE USING (true);
CREATE POLICY "Allow anonymous delete access" ON token_usage FOR DELETE USING (true);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_content_files_updated_at 
    BEFORE UPDATE ON content_files 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional)
-- INSERT INTO content_files (filename, file_type, transcript, processing_status) 
-- VALUES ('sample_video.mp4', 'video', 'This is a sample transcript for testing purposes.', 'completed');
