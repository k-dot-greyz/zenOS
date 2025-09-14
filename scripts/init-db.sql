-- zenOS Database Schema
-- PostgreSQL initialization script

-- Create sessions table for conversation tracking
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create messages table for conversation history
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    model VARCHAR(100),
    tokens_used INTEGER,
    cost DECIMAL(10, 6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create index for faster session queries
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Create contexts table for file and project context
CREATE TABLE IF NOT EXISTS contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('file', 'diff', 'project', 'url', 'custom')),
    name VARCHAR(255) NOT NULL,
    content TEXT,
    embedding vector(384), -- For semantic search (if using pgvector)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create index for context queries
CREATE INDEX IF NOT EXISTS idx_contexts_session_id ON contexts(session_id);
CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(type);

-- Create agents table for custom agents
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    manifest JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    version VARCHAR(20) DEFAULT '1.0.0'
);

-- Create index for agent queries
CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(name);
CREATE INDEX IF NOT EXISTS idx_agents_is_active ON agents(is_active);

-- Create usage_stats table for tracking
CREATE TABLE IF NOT EXISTS usage_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    model VARCHAR(100) NOT NULL,
    requests INTEGER DEFAULT 0,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 6) DEFAULT 0,
    errors INTEGER DEFAULT 0,
    avg_latency_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, model)
);

-- Create index for usage queries
CREATE INDEX IF NOT EXISTS idx_usage_stats_date ON usage_stats(date);
CREATE INDEX IF NOT EXISTS idx_usage_stats_model ON usage_stats(model);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default system agent
INSERT INTO agents (name, description, manifest, created_by) VALUES
(
    'system',
    'Default system agent for general queries',
    '{
        "name": "system",
        "description": "Default system agent",
        "version": "1.0.0",
        "capabilities": ["general", "coding", "analysis"],
        "model_preference": "balanced"
    }'::jsonb,
    'system'
)
ON CONFLICT (name) DO NOTHING;

-- Create view for session summaries
CREATE OR REPLACE VIEW session_summaries AS
SELECT 
    s.id,
    s.title,
    s.created_at,
    s.updated_at,
    COUNT(m.id) as message_count,
    SUM(m.tokens_used) as total_tokens,
    SUM(m.cost) as total_cost,
    MAX(m.created_at) as last_message_at
FROM sessions s
LEFT JOIN messages m ON s.id = m.session_id
GROUP BY s.id, s.title, s.created_at, s.updated_at;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO zen;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO zen;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO zen;
