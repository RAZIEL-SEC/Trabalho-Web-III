# Contrato da API: cadastro e listagem de itens

## Autenticação por cookie

`GET /itens` e `POST /itens` exigem um usuário ativo, autenticado pela
dependência existente `get_usuario_atual`. A autenticação atual permanece em
uso; a decisão sobre Auth0 aguarda alinhamento com João.

Faça login com o usuário previamente cadastrado:

```http
POST /auth/login
Content-Type: application/json

{"email": "usuario@example.org", "senha": "<senha-do-usuario>"}
```

Resposta `200 OK`:

```json
{"id": 7, "nome": "Usuário Exemplo", "email": "usuario@example.org"}
```

A resposta define o cookie `access_token`, com `HttpOnly`, `SameSite=strict`
e `Path=/`. A opção `Secure` depende de `COOKIE_SECURE` na configuração.
O prazo é definido por `ACCESS_TOKEN_MINUTES`; respostas autenticadas
bem-sucedidas renovam o cookie. A API não devolve o token no corpo JSON.

O navegador deve guardar e reenviar o cookie. Exemplo para frontend na mesma
origem da API:

```javascript
await fetch("/auth/login", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, senha }),
});

const resposta = await fetch("/itens?limite=20&offset=0", {
  credentials: "include",
});
```

Sem cookie válido ou com usuário inativo, as duas rotas retornam `401`:

```json
{"detail": "Não autenticado"}
```

O login retorna `401` para credenciais inválidas ou usuário inativo, `422`
para dados fora do contrato e `429` após cinco falhas por IP e e-mail na janela
de dez minutos. Credenciais inválidas usam a mensagem
`{"detail": "E-mail ou senha incorretos"}`.

## Cadastrar item

```http
POST /itens
Content-Type: application/json
Cookie: access_token=<cookie-recebido-no-login>

{"nome": "Arroz", "unidade": "kg"}
```

O corpo aceita somente os dois campos obrigatórios:

| Campo | Tipo | Regras |
| --- | --- | --- |
| `nome` | string | Remove espaços no início e no fim; deve ter de 1 a 100 caracteres após essa remoção. |
| `unidade` | string | Somente `kg`, `un`, `l` ou `pacote`, exatamente nessa grafia. |

Campos extras são recusados, inclusive `saldo`, `ativo`, `criado_por`, `id`
e `criado_em`. Nome vazio ou composto somente de espaços também é recusado.
O backend define `criado_por` pelo usuário autenticado, e o banco fornece
`saldo = 0`, `ativo = true`, identificador e data de criação.

Resposta `201 Created`:

```json
{
  "id": 12,
  "nome": "Arroz",
  "unidade": "kg",
  "saldo": "0.00",
  "ativo": true,
  "criado_por": 7,
  "criado_em": "2026-10-31T15:00:00Z"
}
```

`criado_em` é uma data/hora ISO 8601 com fuso. Os identificadores e a data
acima são ilustrativos.

O par `(nome, unidade)` deve ser único. Por exemplo, um segundo cadastro
de `Arroz`/`kg`, inclusive com espaços nas extremidades do nome, retorna
`409 Conflict`:

```json
{"detail": "Já existe um item com esse nome e unidade."}
```

Nesse caso, a transação é revertida e o item original é preservado.
O mesmo nome com outra unidade pode ser cadastrado.

Dados inválidos retornam `422 Unprocessable Entity`, sem criar registros.
Exemplo de resposta para `{"nome": "Arroz", "unidade": "caixa"}`:

```json
{
  "detail": [
    {
      "type": "literal_error",
      "loc": ["body", "unidade"],
      "msg": "Input should be 'kg', 'un', 'l' or 'pacote'",
      "input": "caixa",
      "ctx": {"expected": "'kg', 'un', 'l' or 'pacote'"}
    }
  ]
}
```

O frontend deve usar o status e `detail[].loc`/`detail[].type` para tratar
erros de validação, sem depender do texto de `msg`.

## Listar itens e paginar

```http
GET /itens?limite=20&offset=0
Cookie: access_token=<cookie-recebido-no-login>
```

| Parâmetro | Tipo | Padrão | Limites |
| --- | --- | --- | --- |
| `limite` | inteiro | `100` | De `1` a `200`, inclusive. |
| `offset` | inteiro | `0` | Maior ou igual a `0`. |

Retorna `200 OK` com um array de itens no mesmo formato do cadastro:

```json
[
  {
    "id": 12,
    "nome": "Arroz",
    "unidade": "kg",
    "saldo": "0.00",
    "ativo": true,
    "criado_por": 7,
    "criado_em": "2026-10-31T15:00:00Z"
  }
]
```

A ordenação é por `nome` e, em caso de empate, por `id`. Não há envelope,
total de registros ou filtro por usuário: a listagem inclui os itens
cadastrados, também sem filtro por `ativo`. Uma página sem registros retorna
`[]`. Para a próxima página, avance `offset` pelo valor de `limite`.
Parâmetros fora dos limites ou que não representam inteiros retornam `422`.

## Saldo Decimal no JSON

`saldo` é um `Decimal` no backend, armazenado como `NUMERIC(10,2)` no
PostgreSQL. Nas respostas das duas rotas, ele é serializado como **string**,
por exemplo `"0.00"`, e não como número JSON. O frontend deve tipar o campo
como `string` e preservar a representação decimal; conversões para ponto
flutuante podem perder precisão. O cadastro não aceita saldo enviado pelo
cliente.

## Códigos de resposta

| Rota | Sucesso | Erros previstos |
| --- | --- | --- |
| `POST /auth/login` | `200` | `401` credenciais/usuário; `422` validação; `429` limite de tentativas. |
| `POST /itens` | `201` | `401` autenticação; `409` par nome/unidade duplicado; `422` validação. |
| `GET /itens` | `200` | `401` autenticação; `422` paginação inválida. |

## Verificação

Os testes de integração em `backend/tests/test_itens.py` usam PostgreSQL
real, login por `/auth/login` e o cookie recebido. Apenas a conexão de banco
é direcionada para um schema isolado; a autenticação não é substituída.
Comandos, resultados e limites da verificação estão em [testes.md](testes.md).
