-- Proteções de idempotência e limitação de requisições.
-- Execute uma única vez em bancos já existentes.
BEGIN;

CREATE TABLE IF NOT EXISTS idempotency_keys (
    id              BIGSERIAL PRIMARY KEY,
    usuario_id      INTEGER NOT NULL,
    idempotency_key UUID NOT NULL,
    request_hash    CHAR(64) NOT NULL,
    response_body   JSONB,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_idempotency_usuario_key UNIQUE (usuario_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_idempotency_criado_em
    ON idempotency_keys (criado_em);

CREATE TABLE IF NOT EXISTS rate_limit_counters (
    bucket_key      VARCHAR(80) PRIMARY KEY,
    window_start    TIMESTAMPTZ NOT NULL,
    request_count   INTEGER NOT NULL CHECK (request_count > 0)
);

COMMIT;
