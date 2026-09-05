-- ============================================================
-- Referral Guardian — Supabase Schema Alignment Migration
-- Run this in: Supabase Dashboard > SQL Editor
-- ============================================================

-- 1. case_events: add missing columns (timestamp, details)
ALTER TABLE case_events
    ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS details TEXT;

-- Backfill timestamp from created_at if it exists
UPDATE case_events SET timestamp = created_at WHERE timestamp IS NULL;

-- 2. bottlenecks: create table if missing (or add missing columns)
CREATE TABLE IF NOT EXISTS bottlenecks (
    id              TEXT PRIMARY KEY,
    case_id         TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    run_id          TEXT,
    bottleneck_type TEXT NOT NULL,
    description     TEXT,
    severity        TEXT,
    detected_at     TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE bottlenecks
    ADD COLUMN IF NOT EXISTS run_id TEXT,
    ADD COLUMN IF NOT EXISTS bottleneck_type TEXT,
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS severity TEXT,
    ADD COLUMN IF NOT EXISTS detected_at TIMESTAMPTZ DEFAULT NOW();

-- 3. agent_recommendations: create table if missing (or add missing columns)
CREATE TABLE IF NOT EXISTS agent_recommendations (
    id                    TEXT PRIMARY KEY,
    case_id               TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    run_id                TEXT,
    bottleneck            TEXT NOT NULL,
    confidence            FLOAT NOT NULL,
    recommended_action    TEXT NOT NULL,
    priority              TEXT NOT NULL,
    reason                TEXT NOT NULL,
    evidence              TEXT,
    status                TEXT DEFAULT 'PENDING',
    human_modified_action TEXT,
    approval_timestamp    TIMESTAMPTZ,
    approver_id           TEXT,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE agent_recommendations
    ADD COLUMN IF NOT EXISTS run_id TEXT,
    ADD COLUMN IF NOT EXISTS bottleneck TEXT,
    ADD COLUMN IF NOT EXISTS confidence FLOAT,
    ADD COLUMN IF NOT EXISTS recommended_action TEXT,
    ADD COLUMN IF NOT EXISTS priority TEXT,
    ADD COLUMN IF NOT EXISTS reason TEXT,
    ADD COLUMN IF NOT EXISTS evidence TEXT,
    ADD COLUMN IF NOT EXISTS human_modified_action TEXT,
    ADD COLUMN IF NOT EXISTS approval_timestamp TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS approver_id TEXT;

-- ============================================================
-- After running: go to Supabase Dashboard > Settings > API
-- and click "Reload schema" (or wait ~30s for cache to refresh)
-- ============================================================
