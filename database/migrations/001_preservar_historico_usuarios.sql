-- Permite excluir contas sem remover ou reescrever seus registros históricos.
-- Execute uma única vez no banco existente; IF EXISTS torna a operação repetível.
BEGIN;

ALTER TABLE auditoria
    DROP CONSTRAINT IF EXISTS auditoria_usuario_id_fkey;

ALTER TABLE itens
    DROP CONSTRAINT IF EXISTS itens_criado_por_fkey;

ALTER TABLE movimentacoes
    DROP CONSTRAINT IF EXISTS movimentacoes_usuario_id_fkey;

COMMIT;
