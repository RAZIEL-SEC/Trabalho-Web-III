-- Amplia as unidades de medida aceitas para itens de estoque.
-- Seguro para bancos existentes e reexecução pelo app.migrate.
ALTER TABLE itens
    DROP CONSTRAINT IF EXISTS itens_unidade_check,
    DROP CONSTRAINT IF EXISTS ck_itens_unidade_valida;

ALTER TABLE itens
    ADD CONSTRAINT ck_itens_unidade_valida
    CHECK (unidade IN ('kg', 'g', 'un', 'l', 'ml', 'pacote', 'garrafa', 'frasco', 'lata', 'caixa', 'fardo', 'kit', 'par', 'rolo', 'duzia', 'bandeja', 'saco', 'galao'));
