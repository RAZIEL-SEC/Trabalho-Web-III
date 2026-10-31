# Verificação do cadastro e da listagem de itens

Verificação realizada em 31/10/2026, na branch `desenvolvimento`.

## Ambiente e execução

- Python `3.13.17`, no ambiente `.venv` da raiz.
- FastAPI `0.162.0`, Pydantic `2.14.2`, SQLAlchemy `2.1.6`, psycopg `3.3.6`,
  pytest `9.2.0` e HTTPX `0.28.1`.
- PostgreSQL configurado pelo `backend/.env` existente. Senhas, chaves e
  cookies não foram registrados neste documento.

Comandos executados a partir de `backend/`, no PowerShell:

```powershell
../.venv/Scripts/python.exe -m pytest tests/test_itens.py -q --tb=short
```

Resultado final: **44 testes passaram**, com um aviso de depreciação, em `4,53 s`.

```powershell
../.venv/Scripts/python.exe -m pytest tests -q --tb=short
```

Resultado final da suíte completa: **44 testes passaram**, com um aviso de
depreciação, em `4,97 s`.

Na raiz, também foram executados `git status --short`, `git diff`,
`git diff --cached` e `git diff --check` para conferir as alterações existentes
e revisar os arquivos da entrega. A checagem de espaços não apontou erros.

## Isolamento dos dados

Cada teste cria um schema PostgreSQL com nome aleatório `test_itens_*`, dentro
de uma transação externa. O schema recebe as tabelas, sequências, índices e
triggers definidos em `database/schema.sql`. O `search_path` contém apenas
esse schema, impedindo que os testes busquem tabelas no schema `public`.

A fixture substitui somente `get_db`. O login, a verificação Argon2id, a
emissão/leitura do cookie e `get_usuario_atual` executam o código real da
aplicação. O cliente usa uma URL HTTPS em processo para aceitar também
cookies `Secure`, sem modificar a configuração existente.

A sessão usa `join_transaction_mode="create_savepoint"`: os commits e
rollbacks das rotas são executados, mas não encerram a transação externa.
Ao final, o rollback externo desfaz o schema inteiro, incluindo usuários,
itens e sequências de teste. A fixture verifica que o schema deixou de existir.
Não são executados `TRUNCATE`, exclusão de registros existentes ou alterações
nas tabelas públicas. A senha de teste é gerada a cada execução.

É necessário que a conta do banco tenha permissão de criar schemas; a falta
dessa permissão faz os testes falharem, sem recorrer às tabelas públicas.

## Comportamento efetivamente testado

| Verificação | Resultado |
| --- | --- |
| `GET /itens` e `POST /itens` sem autenticação | `401`, sem criar itens. |
| Login por `POST /auth/login` com usuário e senha reais de teste | `200`, cookie recebido e acesso às duas rotas permitido. |
| Cookie do login | `HttpOnly`, `SameSite=strict`, `Path=/`. |
| Senha incorreta | Login `401`; as duas rotas continuam protegidas. |
| Cookie inválido ou usuário desativado após o login | As duas rotas retornam `401`. |
| Cadastro com cada unidade (`kg`, `un`, `l`, `pacote`) | `201`; dados recarregados do PostgreSQL. |
| Valores definidos pelo servidor | Saldo `Decimal("0.00")`, ativo e `criado_por` do usuário autenticado. |
| Troca de usuário pelo login real | O novo item pertence ao segundo usuário autenticado, sem id de autor fixo. |
| Nome com espaços nas extremidades | Espaços removidos antes de persistir. |
| Data de criação e saldo no JSON | Data com fuso; saldo como string `"0.00"`. |
| Mesmo nome e unidade, inclusive após remover espaços | `409`, um só registro; sessão continua utilizável após rollback. |
| Cadastro após uma duplicidade | `201`, confirmando recuperação da transação. |
| Mesmo nome com unidades diferentes | Permitido, com dois registros. |
| Nome vazio, em branco, com 101 caracteres, nulo, numérico ou ausente | `422`, sem registros novos. |
| Unidade ausente, nula, desconhecida ou em maiúsculas | `422`, sem registros novos. |
| Campos extras `saldo`, `ativo`, `criado_por`, `id`, `criado_em`, `outro` | `422`, sem registros novos. |
| Nome com 100 caracteres | `201`. |
| Listagem dos itens cadastrados | `200`, ordenada por nome e id, com saldo string. |
| Paginação com 205 itens isolados | Padrão de 100, máximo de 200, offset intermediário, último item e página vazia confirmados. |
| Limites 0, negativo, acima de 200 ou não inteiro; offset negativo ou não inteiro | `422`. |
| Limpeza após cada teste | Schema de teste não existe após rollback. |

Também foi executado um script Python via entrada padrão, a partir de
`backend/`, usando `../.venv/Scripts/python.exe -`. Ele iniciou a aplicação
com `TestClient`, sem substituir dependências, e confirmou:

- `GET /saude`: `200`, com `{"status": "ok"}`, executando `SELECT 1`.
- Existência de `public.usuarios`, `public.itens` e `public.movimentacoes`
  por consulta a `information_schema.tables`.
- Contagem anterior aos testes: 1 usuário, 1 item e 0 movimentações.

Depois da suíte completa, outro script via entrada padrão consultou as mesmas
contagens e `pg_namespace`: permaneceram **1 usuário, 1 item e 0 movimentações**
no schema público, e **nenhum schema `test_itens_*`** ficou no banco.

## Avisos e limites da verificação

O ambiente emite um `StarletteDeprecationWarning`: o uso de HTTPX pelo
`TestClient` está depreciado nessa versão e recomenda `httpx2`. Os testes
passaram com as dependências já instaladas. A atualização dessas dependências
fica pendente e não faz parte desta entrega.

Não foram verificados nesta entrega: chamadas pelo navegador/frontend,
CORS entre origens, HTTPS em servidor externo, expiração temporal do cookie,
limite de tentativas do login, Auth0, movimentações de estoque ou estornos.
Os testes de integração usam HTTP em processo via `TestClient`, com banco
PostgreSQL real; não validam a implantação em rede.

Os demais arquivos `test_auth.py`, `test_estoque.py` e `test_estorno.py`
continuam como placeholders. Sua presença não representa cobertura dessas
funcionalidades.

## Movimentações: entrada e saída (31/10/2026)

Esta rodada complementa a entrega de itens descrita acima. As pendências
citadas naquela entrega se referem à verificação anterior; os resultados
atuais de movimentações estão nesta seção. A revisão da contagem e a
restauração de cobertura de itens estão descritas ao final.

Comandos executados a partir de `backend/`, no PowerShell:

```powershell
../.venv/Scripts/python.exe -m pytest tests/test_movimentacoes.py -q --tb=short
```

Resultado: **54 testes passaram**, com o aviso de depreciação já descrito,
em `9,31 s`.

```powershell
../.venv/Scripts/python.exe -m pytest tests/test_movimentacoes_concorrencia.py -q --tb=short
```

Resultado: **6 testes passaram**, com o mesmo aviso, em `2,41 s`.

Primeira execução da suíte completa, incluindo os 43 testes de itens presentes
no início da implementação, antes da revisão de cobertura:

```powershell
../.venv/Scripts/python.exe -m pytest tests -q --tb=short
```

Resultado: **103 testes passaram**, com um aviso de depreciação, em `16,85 s`.
São 43 testes de itens e 60 testes novos de movimentações. `git diff --check`
também foi executado na raiz e não apontou erros de espaços.

### Verificações executadas no PostgreSQL real

| Verificação | Resultado |
| --- | --- |
| Sem autenticação, cookie inválido ou usuário inativo | `POST /movimentacoes` retorna `401`. |
| Login real e cookie recebido | Permitem movimentar; autenticação não foi substituída. |
| Entradas com quantidades decimais, inteiras e zeros finais | `201`, saldo somado e histórico persistido, com duas casas no JSON. |
| Saídas parciais e de todo o saldo | `201`, quantidade positiva no histórico e saldo subtraído até zero. |
| Sequência `0.10 + 0.20 - 0.10` | Saldo exato `"0.20"`. |
| Persistência | Item e movimentação recarregados do PostgreSQL; `GET /itens` reflete o saldo. |
| Troca de usuário por outro login real | `usuario_id` vem do novo cookie; autor original do item é preservado. |
| Saldo insuficiente ou zero para saída | `409`, saldo e histórico preservados; nova operação válida continua possível. |
| Item inexistente | `404`, sem histórico novo. |
| Item inativo | `409` tanto para entrada quanto para saída. |
| Saldo máximo `99999999.99` | Permitido; entrada adicional de `0.01` retorna `409` sem alterar os dados. |
| Quantidade inválida, zero, negativa, com excesso de casas/dígitos, NaN ou infinita | `422`, saldo e histórico preservados. |
| Identificador inválido, tipo inválido/estorno, observação inválida e campos extras | `422`, sem alteração dos dados. |
| Campos obrigatórios ausentes | `422`. |
| Falha real ao inserir histórico, em entrada e saída | Rollback também reverte a alteração do saldo; nova operação funciona após remover o trigger de teste. |
| Falha real no `COMMIT`, em entrada e saída | Saldo e histórico anteriores preservados; requisição seguinte pode concluir. |
| Duas entradas simultâneas | Ambas `201`, sem perda de atualização; saldo `5.50`. |
| Duas saídas disputando saldo insuficiente para ambas | Uma `201`, outra `409`; saldo `1.00`, sem saída duplicada. |
| Duas saídas com saldo suficiente | Ambas `201`, saldo final correto `3.00`. |
| Entrada e saída simultâneas | Ambas `201`, saldo final correto `3.00`. |

Os testes sequenciais usam a fixture transacional já descrita, com schemas
`test_itens_*`, savepoints e rollback externo. As falhas de inserção são
provocadas por um trigger real, criado somente no schema do teste.

Os testes com conexões independentes criam um schema aleatório
`test_concorrencia_*` e confirmam sua criação para que as conexões o enxerguem.
Cada requisição recebe sua própria sessão, sem substituir `get_usuario_atual`.
O schema é removido no `finally`, e sua ausência é conferida. `SET LOCAL` é
aplicado a cada transação para isolar o schema e não modificar as conexões
devolvidas ao pool. Nenhuma tabela pública é usada para gravação.

Para verificar concorrência, uma conexão segura o bloqueio do item enquanto
duas requisições reais chegam ao banco. A consulta a `pg_stat_activity`
confirma que ambas aguardam bloqueio antes da liberação; o teste não presume
concorrência apenas pelo tempo decorrido. Há timeouts locais aos testes.
O saldo final também é comparado com a soma do histórico confirmado.

Para exercitar falha no `COMMIT`, um constraint trigger
`DEFERRABLE INITIALLY DEFERRED` falha na confirmação da transação real,
depois do flush. Esse caso usa o schema com conexões independentes, pois o
commit de um savepoint não confirma a transação externa.

Antes e depois desta rodada, um script Python executado via entrada padrão
com `../.venv/Scripts/python.exe -`, a partir de `backend/`, consultou as
contagens das tabelas públicas. Permaneceram **1 usuário, 1 item e 0
movimentações**. Depois da suíte, `pg_namespace` confirmou **zero schemas
`test_itens_*` ou `test_concorrencia_*` restantes**. O script final também
iniciou a aplicação via `TestClient`, sem overrides de dependências, e
confirmou `GET /saude`: **200**, com `{"status": "ok"}`.

Não foram verificados nesta rodada: navegador/frontend, CORS, implantação
em rede, expiração de cookies, limite de tentativas de login e estornos.
Não há integração com Auth0 nem alteração da autenticação atual. Não foi
necessária migração do banco. Os testes usam a configuração existente em
`backend/.env`, sem exibir segredos.

### Revisão antes do commit: contagem e cobertura

O commit de itens `d31e91b` continha 44 testes. Antes da implementação de
movimentações, já existia uma alteração local removendo
`test_cadastro_usa_usuario_do_cookie` de `backend/tests/test_itens.py`.
Essa remoção explica a primeira execução de 43 testes de itens e o total
intermediário de 103; não houve falha, skip ou mudança de parametrização.

O teste removido faz login como um segundo usuário, cadastra um novo item e
confirma no JSON e no PostgreSQL que `criado_por` corresponde a esse usuário.
`test_autor_vem_do_usuario_do_cookie`, dos testes de movimentações, verifica
`usuario_id` da movimentação e preservação do autor do item existente; ele
não substitui a cobertura de autoria de um novo cadastro de item.

A revisão restaurou integralmente o teste de itens do commit `d31e91b`.
Assim, `backend/tests/test_itens.py` voltou ao conteúdo já commitado e sua
remoção não integra esta entrega. O registro original de 44 testes foi
restabelecido na seção histórica de itens. O resultado de 103 acima permanece
identificado como a execução anterior à revisão.

Após a restauração, foram executados, a partir de `backend/`:

```powershell
../.venv/Scripts/python.exe -m pytest tests/test_itens.py -q --tb=short
```

Resultado: **44 testes passaram**, um aviso de depreciação, em `4,87 s`.

```powershell
../.venv/Scripts/python.exe -m pytest tests -q --tb=short
```

Resultado final da revisão: **104 testes passaram**, um aviso de depreciação,
em `12,01 s`: **44 de itens + 54 sequenciais de movimentações + 6 de
concorrência/commit real**. O aviso continua sendo o `StarletteDeprecationWarning`
sobre HTTPX; não houve falhas nem testes ignorados.

O contrato foi comparado com os modelos de entrada e resposta, a autenticação,
as regras de saldo, os erros e os testes executados. Ele mantém os valores
decimais como strings, explicita os limites e a precisão e diferencia o saldo
após uma movimentação do saldo obtido em uma consulta posterior. Permanecem
fora da verificação as integrações de frontend e os demais limites já listados.

A conferência após esta revisão repetiu `GET /saude` sem overrides: `200`,
com `{"status": "ok"}`. As tabelas públicas permaneceram com 1 usuário,
1 item e 0 movimentações, e não restaram schemas de teste.
