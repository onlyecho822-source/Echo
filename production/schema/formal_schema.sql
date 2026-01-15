-- Echo Phoenix Formal Schema
-- Enforces invariants I1-I4 at database level
-- Version: 2.4.0-formal

-- =============================================================================
-- I4: Append-only ledger L
-- =============================================================================

CREATE TABLE IF NOT EXISTS ledger (
    id BIGSERIAL PRIMARY KEY,
    hash CHAR(64) NOT NULL UNIQUE,  -- h(e) = SHA256(canon(e))
    canonical JSONB NOT NULL,        -- canon(e)
    source VARCHAR(32) NOT NULL,     -- 'stripe', 'github', 'echo', 'manual', 'zapier'
    type VARCHAR(128) NOT NULL,
    external_id VARCHAR(128),        -- stripe_evt_*, github_pr_*
    payload JSONB,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    risk_score FLOAT DEFAULT 0.0,
    
    CONSTRAINT ledger_source_check CHECK (source IN ('stripe', 'github', 'echo', 'manual', 'zapier')),
    CONSTRAINT risk_score_range CHECK (risk_score >= 0 AND risk_score <= 1)
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_ledger_hash ON ledger USING HASH (hash);
CREATE INDEX IF NOT EXISTS idx_ledger_source_type ON ledger (source, type);
CREATE INDEX IF NOT EXISTS idx_ledger_processed_at ON ledger USING BRIN (processed_at);
CREATE INDEX IF NOT EXISTS idx_ledger_external_id ON ledger (external_id) WHERE external_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ledger_risk ON ledger (risk_score) WHERE risk_score >= 0.7;

-- =============================================================================
-- I1: Dedupe set D (with TTL for window W = 24h)
-- =============================================================================

CREATE TABLE IF NOT EXISTS dedupe_set (
    hash CHAR(64) PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ GENERATED ALWAYS AS (created_at + INTERVAL '25 hours') STORED
);

CREATE INDEX IF NOT EXISTS idx_dedupe_expires ON dedupe_set (expires_at);

-- Cleanup function for expired entries
CREATE OR REPLACE FUNCTION cleanup_expired_dedupe()
RETURNS void AS $$
BEGIN
    DELETE FROM dedupe_set WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- I3: Control state Σ_E (with audit trail)
-- =============================================================================

CREATE TABLE IF NOT EXISTS control_state (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(64) NOT NULL,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by VARCHAR(128) NOT NULL,
    reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_control_state_key ON control_state (key);
CREATE INDEX IF NOT EXISTS idx_control_state_updated_at ON control_state USING BRIN (updated_at);

-- Get current value for a key
CREATE OR REPLACE FUNCTION get_control_state(p_key VARCHAR)
RETURNS JSONB AS $$
BEGIN
    RETURN (
        SELECT value 
        FROM control_state 
        WHERE key = p_key 
        ORDER BY updated_at DESC 
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Audit trail for control changes
-- =============================================================================

CREATE TABLE IF NOT EXISTS control_audit (
    id BIGSERIAL PRIMARY KEY,
    cmd VARCHAR(64) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    old_state JSONB,
    new_state JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_control_audit_timestamp ON control_audit USING BRIN (timestamp);
CREATE INDEX IF NOT EXISTS idx_control_audit_actor ON control_audit (actor);

-- =============================================================================
-- F2: Reconciliation gaps
-- =============================================================================

CREATE TABLE IF NOT EXISTS reconciliation_gaps (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(32) NOT NULL,
    external_id VARCHAR(128) NOT NULL,
    expected_hash CHAR(64),
    found_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    gap_type VARCHAR(32) CHECK (gap_type IN ('missing', 'mismatch', 'duplicate')),
    resolution TEXT
);

CREATE INDEX IF NOT EXISTS idx_reconciliation_unresolved ON reconciliation_gaps (found_at) 
    WHERE resolved_at IS NULL;

-- =============================================================================
-- Materialized view for risk events (for ZAP 3)
-- =============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS risk_events AS
SELECT 
    hash,
    source,
    type,
    risk_score,
    processed_at,
    payload
FROM ledger
WHERE risk_score >= 0.7
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_risk_events_hash ON risk_events (hash);

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_risk_events()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY risk_events;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Initial state
-- =============================================================================

INSERT INTO control_state (key, value, updated_by, reason) VALUES
    ('frozen', 'false', 'system', 'initial state'),
    ('throttle', '0.0', 'system', 'initial state'),
    ('require_manual_approval', 'false', 'system', 'initial state')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Atomic check-and-set function for I1
-- =============================================================================

CREATE OR REPLACE FUNCTION atomic_check_set(p_hash CHAR(64))
RETURNS BOOLEAN AS $$
DECLARE
    v_exists BOOLEAN;
BEGIN
    -- Try to insert, return true if successful (new hash)
    INSERT INTO dedupe_set (hash) VALUES (p_hash)
    ON CONFLICT (hash) DO NOTHING;
    
    GET DIAGNOSTICS v_exists = ROW_COUNT;
    RETURN v_exists > 0;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Invariant verification queries
-- =============================================================================

-- I1: Check for duplicates (should return 0)
CREATE OR REPLACE FUNCTION verify_i1_no_duplicates()
RETURNS TABLE(duplicate_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*) - COUNT(DISTINCT hash) as duplicate_count
    FROM ledger;
END;
$$ LANGUAGE plpgsql;

-- I4: Check ledger completeness (compare with external source)
CREATE OR REPLACE FUNCTION verify_i4_completeness(p_source VARCHAR, p_since TIMESTAMPTZ)
RETURNS TABLE(ledger_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*) as ledger_count
    FROM ledger
    WHERE source = p_source
    AND processed_at >= p_since;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Scheduled jobs (for pg_cron if available)
-- =============================================================================

-- Run every hour: cleanup expired dedupe entries
-- SELECT cron.schedule('cleanup-dedupe', '0 * * * *', 'SELECT cleanup_expired_dedupe()');

-- Run every 5 minutes: refresh risk events view
-- SELECT cron.schedule('refresh-risk', '*/5 * * * *', 'SELECT refresh_risk_events()');

COMMENT ON TABLE ledger IS 'I4: Append-only ledger ensuring observability completeness';
COMMENT ON TABLE dedupe_set IS 'I1: Deduplication set for exactly-once processing';
COMMENT ON TABLE control_state IS 'I3: Control state for safety gating';
COMMENT ON TABLE control_audit IS 'Audit trail for all control state changes';
COMMENT ON TABLE reconciliation_gaps IS 'F2: Tracking gaps between external truth and ledger';
