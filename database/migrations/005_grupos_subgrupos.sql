CREATE TABLE IF NOT EXISTS grupos_itens (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS subgrupos_itens (
    id SERIAL PRIMARY KEY,
    grupo_id INTEGER NOT NULL REFERENCES grupos_itens(id),
    nome VARCHAR(80) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_subgrupos_grupo_nome UNIQUE (grupo_id, nome)
);
INSERT INTO grupos_itens (nome) VALUES ('Sem classificação')
ON CONFLICT DO NOTHING;
INSERT INTO subgrupos_itens (grupo_id, nome)
SELECT id, 'Sem classificação' FROM grupos_itens WHERE nome = 'Sem classificação'
ON CONFLICT DO NOTHING;
ALTER TABLE itens ADD COLUMN IF NOT EXISTS subgrupo_id INTEGER;
UPDATE itens SET subgrupo_id = (
    SELECT s.id FROM subgrupos_itens s
    JOIN grupos_itens g ON g.id = s.grupo_id
    WHERE g.nome = 'Sem classificação' AND s.nome = 'Sem classificação'
) WHERE subgrupo_id IS NULL;
ALTER TABLE itens ALTER COLUMN subgrupo_id SET NOT NULL;
DO $$ BEGIN
    ALTER TABLE itens ADD CONSTRAINT fk_itens_subgrupo
        FOREIGN KEY (subgrupo_id) REFERENCES subgrupos_itens(id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
CREATE INDEX IF NOT EXISTS idx_itens_subgrupo_ativo ON itens (subgrupo_id) WHERE ativo IS TRUE;
