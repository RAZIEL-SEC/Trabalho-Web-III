-- Permite reutilizar nomes de classificações desativadas, mantendo unicidade entre registros ativos.
ALTER TABLE grupos_itens DROP CONSTRAINT IF EXISTS grupos_itens_nome_key;
ALTER TABLE subgrupos_itens DROP CONSTRAINT IF EXISTS uq_subgrupos_grupo_nome;

CREATE UNIQUE INDEX IF NOT EXISTS uq_grupos_itens_nome_ativo
    ON grupos_itens (nome)
    WHERE ativo IS TRUE;

CREATE UNIQUE INDEX IF NOT EXISTS uq_subgrupos_grupo_nome_ativo
    ON subgrupos_itens (grupo_id, nome)
    WHERE ativo IS TRUE;
