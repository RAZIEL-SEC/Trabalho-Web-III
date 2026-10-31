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
