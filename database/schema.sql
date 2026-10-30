
-- Sistema de estoque - Amigos do Zé Alguém

CREATE TABLE usuarios (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    senha_hash  TEXT NOT NULL,
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE itens (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    unidade     VARCHAR(10) NOT NULL CHECK (unidade IN ('kg', 'un', 'l', 'pacote')),
    saldo       NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (saldo >= 0),
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    criado_por  INTEGER NOT NULL REFERENCES usuarios(id),
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (nome, unidade)
);

CREATE TABLE movimentacoes (
    id          BIGSERIAL PRIMARY KEY,
    item_id     INTEGER NOT NULL REFERENCES itens(id),
    tipo        VARCHAR(10) NOT NULL CHECK (tipo IN ('entrada', 'saida', 'estorno')),
    quantidade  NUMERIC(10,2) NOT NULL CHECK (quantidade > 0),
    observacao  TEXT,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
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