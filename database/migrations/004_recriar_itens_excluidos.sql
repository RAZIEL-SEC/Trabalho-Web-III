-- Permite recriar um item depois de sua exclusão lógica.
-- Mantém os registros inativos para preservar o histórico de movimentações.
-- Reexecução segura: remove a restrição antiga, se existir, e recria o índice parcial.
ALTER TABLE itens
    DROP CONSTRAINT IF EXISTS itens_nome_unidade_key;

DROP INDEX IF EXISTS uq_itens_nome_unidade_ativos;

CREATE UNIQUE INDEX uq_itens_nome_unidade_ativos
    ON itens (nome, unidade)
    WHERE ativo IS TRUE;
