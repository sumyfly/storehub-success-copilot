-- Customer Success Copilot Database Schema
-- PostgreSQL initialization script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE alert_type AS ENUM ('churn_risk', 'upsell_opportunity', 'usage_decline', 'engagement_drop', 'payment_issue');
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_status AS ENUM ('open', 'acknowledged', 'in_progress', 'resolved', 'dismissed');
CREATE TYPE feedback_type AS ENUM ('alert_accuracy', 'alert_relevance', 'action_effectiveness', 'priority_rating');
CREATE TYPE action_outcome AS ENUM ('successful', 'unsuccessful', 'pending', 'cancelled');

-- ============================================================================
-- CUSTOMER MANAGEMENT TABLES
-- ============================================================================

-- Customer master table
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    subscription_tier VARCHAR(50),
    mrr DECIMAL(10,2),
    contract_start_date DATE,
    contract_end_date DATE,
    primary_contact_email VARCHAR(255),
    account_manager VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT customers_external_id_key UNIQUE (external_id)
);

-- Customer health scores table
CREATE TABLE customer_health_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    overall_score DECIMAL(3,2) CHECK (overall_score >= 0 AND overall_score <= 1),
    usage_score DECIMAL(3,2) CHECK (usage_score >= 0 AND usage_score <= 1),
    engagement_score DECIMAL(3,2) CHECK (engagement_score >= 0 AND engagement_score <= 1),
    support_score DECIMAL(3,2) CHECK (support_score >= 0 AND support_score <= 1),
    financial_score DECIMAL(3,2) CHECK (financial_score >= 0 AND financial_score <= 1),
    relationship_score DECIMAL(3,2) CHECK (relationship_score >= 0 AND relationship_score <= 1),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_version VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Indexes
    CONSTRAINT unique_customer_health_timestamp UNIQUE (customer_id, calculated_at)
);

-- Risk assessments table
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    risk_type VARCHAR(50) NOT NULL,
    risk_score DECIMAL(3,2) CHECK (risk_score >= 0 AND risk_score <= 1),
    risk_factors JSONB,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    CONSTRAINT unique_customer_risk_type UNIQUE (customer_id, risk_type, created_at)
);

-- ============================================================================
-- ALERT MANAGEMENT TABLES
-- ============================================================================

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    alert_type alert_type NOT NULL,
    severity alert_severity NOT NULL DEFAULT 'medium',
    status alert_status NOT NULL DEFAULT 'open',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    risk_score DECIMAL(3,2) CHECK (risk_score >= 0 AND risk_score <= 1),
    risk_factors JSONB,
    suggested_actions JSONB,
    assigned_to VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Alert feedback table
CREATE TABLE alert_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    feedback_type feedback_type NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Prevent duplicate feedback from same user on same alert
    CONSTRAINT unique_user_alert_feedback UNIQUE (alert_id, user_id, feedback_type)
);

-- ============================================================================
-- ACTION TRACKING TABLES
-- ============================================================================

-- Customer actions table
CREATE TABLE customer_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    alert_id UUID REFERENCES alerts(id) ON DELETE SET NULL,
    action_type VARCHAR(100) NOT NULL,
    action_details JSONB,
    taken_by VARCHAR(255) NOT NULL,
    taken_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    outcome action_outcome DEFAULT 'pending',
    outcome_details TEXT,
    effectiveness_score DECIMAL(3,2) CHECK (effectiveness_score >= 0 AND effectiveness_score <= 1)
);

-- Action templates table (for suggested actions)
CREATE TABLE action_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    action_type VARCHAR(100) NOT NULL,
    template_data JSONB,
    applicable_risk_types TEXT[],
    applicable_severities alert_severity[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INTEGRATION AND EXTERNAL DATA TABLES
-- ============================================================================

-- Integration configurations
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    integration_type VARCHAR(50) NOT NULL, -- 'crm', 'support', 'analytics', 'billing'
    configuration JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_integration_name UNIQUE (name)
);

-- External system mappings (for ID translations)
CREATE TABLE external_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    internal_id UUID NOT NULL,
    external_system VARCHAR(50) NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'customer', 'contact', 'ticket', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_external_mapping UNIQUE (external_system, external_id, entity_type)
);

-- ============================================================================
-- USER MANAGEMENT AND CONFIGURATION
-- ============================================================================

-- Users table (for CSM and admin users)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'csm', -- 'admin', 'csm', 'manager'
    is_active BOOLEAN DEFAULT TRUE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- System configuration table
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MACHINE LEARNING AND MODEL METADATA
-- ============================================================================

-- Model versions and metadata
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'churn_risk', 'health_score', 'opportunity'
    model_path VARCHAR(500),
    metrics JSONB,
    features JSONB,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deployed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT unique_model_version UNIQUE (name, version)
);

-- Model predictions log (for monitoring and feedback)
CREATE TABLE model_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml_models(id),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    prediction_type VARCHAR(50) NOT NULL,
    prediction_value DECIMAL(10,6),
    prediction_data JSONB,
    features_used JSONB,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Partition by date for performance
    CONSTRAINT model_predictions_date_check CHECK (created_at >= '2024-01-01'::DATE)
) PARTITION BY RANGE (created_at);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Customer indexes
CREATE INDEX idx_customers_external_id ON customers(external_id);
CREATE INDEX idx_customers_account_manager ON customers(account_manager);
CREATE INDEX idx_customers_industry ON customers(industry);

-- Health scores indexes
CREATE INDEX idx_health_scores_customer_id ON customer_health_scores(customer_id);
CREATE INDEX idx_health_scores_calculated_at ON customer_health_scores(calculated_at DESC);
CREATE INDEX idx_health_scores_overall_score ON customer_health_scores(overall_score DESC);

-- Risk assessments indexes
CREATE INDEX idx_risk_assessments_customer_id ON risk_assessments(customer_id);
CREATE INDEX idx_risk_assessments_risk_type ON risk_assessments(risk_type);
CREATE INDEX idx_risk_assessments_risk_score ON risk_assessments(risk_score DESC);

-- Alerts indexes
CREATE INDEX idx_alerts_customer_id ON alerts(customer_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_assigned_to ON alerts(assigned_to);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_alerts_type_severity ON alerts(alert_type, severity);

-- Actions indexes
CREATE INDEX idx_customer_actions_customer_id ON customer_actions(customer_id);
CREATE INDEX idx_customer_actions_alert_id ON customer_actions(alert_id);
CREATE INDEX idx_customer_actions_taken_by ON customer_actions(taken_by);
CREATE INDEX idx_customer_actions_outcome ON customer_actions(outcome);
CREATE INDEX idx_customer_actions_taken_at ON customer_actions(taken_at DESC);

-- Model predictions indexes
CREATE INDEX idx_model_predictions_customer_id ON model_predictions(customer_id);
CREATE INDEX idx_model_predictions_model_id ON model_predictions(model_id);
CREATE INDEX idx_model_predictions_created_at ON model_predictions(created_at DESC);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_action_templates_updated_at BEFORE UPDATE ON action_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default action templates
INSERT INTO action_templates (name, description, action_type, applicable_risk_types, applicable_severities, template_data) VALUES
('Schedule Check-in Call', 'Schedule a 15-minute check-in call to understand customer concerns', 'call', ARRAY['churn_risk', 'engagement_drop'], ARRAY['medium', 'high', 'critical'], '{"duration": "15min", "priority": "high"}'),
('Send Feature Resources', 'Send educational resources about underutilized features', 'email', ARRAY['usage_decline'], ARRAY['low', 'medium'], '{"template": "feature_education", "follow_up_days": 7}'),
('Executive Business Review', 'Schedule EBR to discuss strategic goals and value realization', 'meeting', ARRAY['churn_risk', 'upsell_opportunity'], ARRAY['high', 'critical'], '{"duration": "60min", "attendees": ["executive", "csm", "account_manager"]}'),
('Product Training Session', 'Arrange personalized product training session', 'training', ARRAY['usage_decline', 'engagement_drop'], ARRAY['medium', 'high'], '{"format": "virtual", "duration": "45min"}'),
('Payment Issue Follow-up', 'Contact customer regarding payment or billing concerns', 'call', ARRAY['payment_issue'], ARRAY['high', 'critical'], '{"urgency": "immediate", "escalate_to": "billing_team"}');

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, description) VALUES
('alert_thresholds', '{"churn_risk": {"low": 0.3, "medium": 0.5, "high": 0.7, "critical": 0.9}, "health_score": {"low": 0.4, "medium": 0.6, "high": 0.8}}', 'Risk score thresholds for alert generation'),
('notification_settings', '{"slack_enabled": true, "email_enabled": true, "daily_digest_time": "09:00", "critical_alert_immediate": true}', 'Notification and communication settings'),
('model_settings', '{"retrain_frequency": "weekly", "min_feedback_count": 50, "performance_threshold": 0.8}', 'Machine learning model configuration'),
('dashboard_settings', '{"default_time_range": "30d", "max_alerts_per_page": 25, "auto_refresh_interval": 300}', 'Dashboard and UI configuration');

-- Create initial admin user (password: 'admin123' - should be changed in production)
INSERT INTO users (email, hashed_password, full_name, role) VALUES
('admin@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeqEZKoJB8VyZ6u4G', 'System Administrator', 'admin');

COMMIT; 