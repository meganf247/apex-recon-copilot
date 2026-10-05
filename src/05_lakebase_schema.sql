-- Lakebase (Postgres) operational store for the Reconciliation Workbench.
-- The app reads the synced case queue and writes case state, an audit trail and credit approvals here.

CREATE SCHEMA IF NOT EXISTS recon;

CREATE TABLE IF NOT EXISTS recon.dispute_cases (
    case_id               TEXT PRIMARY KEY,           -- matches gold.dispute_queue.case_id
    billing_month         TEXT        NOT NULL,
    dsp_id                TEXT        NOT NULL,
    deal_id               TEXT        NOT NULL,
    status                TEXT        NOT NULL DEFAULT 'OPEN'
                          CHECK (status IN ('OPEN', 'IN_REVIEW', 'SENT_TO_PARTNER', 'RESOLVED')),
    resolution            TEXT        CHECK (resolution IN ('RECOVERED', 'CREDIT_ISSUED', 'NO_ADJUSTMENT', 'WRITTEN_OFF')),
    owner                 TEXT,
    confirmed_root_cause  TEXT,                       -- analyst's final call; may differ from the model
    revenue_at_risk_usd   NUMERIC(14, 2),
    recovered_usd         NUMERIC(14, 2) DEFAULT 0,
    dispute_email_sent    TEXT,                       -- final edited email body
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recon.case_events (
    event_id    BIGSERIAL PRIMARY KEY,
    case_id     TEXT        NOT NULL REFERENCES recon.dispute_cases (case_id),
    event_type  TEXT        NOT NULL,   -- CREATED, ASSIGNED, STATUS_CHANGED, NOTE, EMAIL_SENT, CREDIT_APPROVED
    actor       TEXT        NOT NULL,
    detail      JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recon.credit_approvals (
    approval_id  BIGSERIAL PRIMARY KEY,
    case_id      TEXT           NOT NULL REFERENCES recon.dispute_cases (case_id),
    amount_usd   NUMERIC(14, 2) NOT NULL CHECK (amount_usd >= 0),
    approved_by  TEXT           NOT NULL,
    reason       TEXT,
    approved_at  TIMESTAMPTZ    NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cases_status ON recon.dispute_cases (status, billing_month);
CREATE INDEX IF NOT EXISTS idx_events_case ON recon.case_events (case_id, created_at);
