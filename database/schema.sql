-- Sistema de estoque - Amigos do Zé Alguém

CREATE TABLE usuarios (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    senha_hash  TEXT NOT NULL,
    perfil      VARCHAR(10) NOT NULL DEFAULT 'operador'
                CHECK (perfil IN ('admin', 'operador')),
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    -- sobe a cada troca de senha, desativação ou "sair de todos os dispositivos":
    -- cookies emitidos com uma versão antiga deixam de valer
    token_versao INTEGER NOT NULL DEFAULT 0,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE grupos_itens (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE subgrupos_itens (
    id SERIAL PRIMARY KEY,
    grupo_id INTEGER NOT NULL REFERENCES grupos_itens(id),
    nome VARCHAR(80) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_subgrupos_grupo_nome UNIQUE (grupo_id, nome)
);

INSERT INTO grupos_itens (nome) VALUES ('Sem classificação');
INSERT INTO subgrupos_itens (grupo_id, nome)
SELECT id, 'Sem classificação' FROM grupos_itens WHERE nome = 'Sem classificação';

CREATE TABLE itens (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    subgrupo_id INTEGER NOT NULL DEFAULT 1,
    unidade     VARCHAR(10) NOT NULL CHECK (unidade IN ('kg', 'g', 'un', 'l', 'ml', 'pacote', 'garrafa', 'frasco', 'lata', 'caixa', 'fardo', 'kit', 'par', 'rolo', 'duzia', 'bandeja', 'saco', 'galao')),
    saldo       NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (saldo >= 0),
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    -- ID histórico do criador; intencionalmente sem FK para usuarios.
    criado_por  INTEGER NOT NULL,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_itens_subgrupo FOREIGN KEY (subgrupo_id) REFERENCES subgrupos_itens(id)
);

-- Só itens ativos precisam ter nome e unidade exclusivos.
-- Itens inativos permanecem para preservar o histórico de movimentações.
CREATE INDEX idx_itens_subgrupo_ativo ON itens (subgrupo_id) WHERE ativo IS TRUE;

CREATE UNIQUE INDEX uq_itens_nome_unidade_ativos
    ON itens (nome, unidade)
    WHERE ativo IS TRUE;

CREATE TABLE movimentacoes (
    id          BIGSERIAL PRIMARY KEY,
    item_id     INTEGER NOT NULL REFERENCES itens(id),
    tipo        VARCHAR(10) NOT NULL CHECK (tipo IN ('entrada', 'saida', 'estorno')),
    quantidade  NUMERIC(10,2) NOT NULL CHECK (quantidade > 0),
    observacao  TEXT,
    -- ID histórico do autor; intencionalmente sem FK para usuarios.
    usuario_id  INTEGER NOT NULL,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    estorno_de  BIGINT REFERENCES movimentacoes(id),
    motivo      TEXT,
    -- estorno exige o original e o motivo; os outros tipos não podem ter
    CHECK ((tipo = 'estorno') = (estorno_de IS NOT NULL)),
    CHECK (tipo <> 'estorno' OR motivo IS NOT NULL)
);

-- um lançamento só pode ser estornado uma vez
CREATE UNIQUE INDEX uq_estorno_unico
    ON movimentacoes (estorno_de) WHERE estorno_de IS NOT NULL;

CREATE INDEX idx_mov_item_data ON movimentacoes (item_id, criado_em DESC);
CREATE INDEX idx_mov_data      ON movimentacoes (criado_em DESC);

-- histórico imutável: correção só por estorno, nunca por edição ou exclusão
CREATE FUNCTION bloquear_alteracao() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'movimentacoes é imutável: use estorno';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_movimentacoes_imutavel
    BEFORE UPDATE OR DELETE ON movimentacoes
    FOR EACH ROW EXECUTE FUNCTION bloquear_alteracao();

-- registro de ações de segurança e administração (logins, usuários, senhas)
CREATE TABLE auditoria (
    id          BIGSERIAL PRIMARY KEY,
    -- ID histórico; NULL continua permitido para e-mail desconhecido no login.
    usuario_id  INTEGER,
    acao        VARCHAR(40) NOT NULL,
    detalhe     TEXT,
    ip          VARCHAR(45),
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_auditoria_data    ON auditoria (criado_em DESC);
CREATE INDEX idx_auditoria_usuario ON auditoria (usuario_id, criado_em DESC);

-- o log não pode ser alterado nem apagado
CREATE FUNCTION auditoria_imutavel() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'auditoria é imutável';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auditoria_imutavel
    BEFORE UPDATE OR DELETE ON auditoria
    FOR EACH ROW EXECUTE FUNCTION auditoria_imutavel();


-- Chaves de idempotência: uma operação de estoque por usuário/chave.
CREATE TABLE idempotency_keys (
    id              BIGSERIAL PRIMARY KEY,
    usuario_id      INTEGER NOT NULL,
    idempotency_key UUID NOT NULL,
    request_hash    CHAR(64) NOT NULL,
    response_body   JSONB,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_idempotency_usuario_key UNIQUE (usuario_id, idempotency_key)
);

CREATE INDEX idx_idempotency_criado_em
    ON idempotency_keys (criado_em);

-- Contadores compartilhados entre workers para rate limiting por usuário/IP.
CREATE TABLE rate_limit_counters (
    bucket_key      VARCHAR(80) PRIMARY KEY,
    window_start    TIMESTAMPTZ NOT NULL,
    request_count   INTEGER NOT NULL CHECK (request_count > 0)
);
