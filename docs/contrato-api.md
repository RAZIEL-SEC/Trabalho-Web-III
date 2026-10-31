# Contrato da API: itens e movimentações de estoque

## Autenticação por cookie

`GET /itens`, `POST /itens` e `POST /movimentacoes` exigem um usuário ativo,
autenticado pela dependência existente `get_usuario_atual`. A autenticação
atual permanece em uso; a decisão sobre Auth0 aguarda alinhamento com João.

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

Sem cookie válido ou com usuário inativo, essas rotas retornam `401`:

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
PostgreSQL. Nas respostas de itens, ele é serializado como **string**,
por exemplo `"0.00"`, e não como número JSON. O frontend deve tipar o campo
como `string` e preservar a representação decimal; conversões para ponto
flutuante podem perder precisão. O cadastro não aceita saldo enviado pelo
cliente.

## Registrar entrada ou saída

```http
POST /movimentacoes
Content-Type: application/json
Cookie: access_token=<cookie-recebido-no-login>

{
  "item_id": 12,
  "tipo": "entrada",
  "quantidade": "10.50",
  "observacao": "Doação recebida"
}
```

| Campo | Tipo | Regras |
| --- | --- | --- |
| `item_id` | inteiro JSON | Obrigatório, de `1` a `2147483647`; deve referenciar um item ativo. Strings, booleanos e números fracionários são recusados. |
| `tipo` | string | Obrigatório: somente `entrada` ou `saida`, exatamente nessa grafia. |
| `quantidade` | string decimal ou número JSON | Obrigatória, positiva, até `99999999.99`, com no máximo duas casas decimais após desconsiderar zeros finais. Recomenda-se enviar string para preservar a precisão. |
| `observacao` | string ou `null` | Opcional, padrão `null`; até 1000 caracteres após remover espaços das extremidades. |

Casas decimais adicionais contendo apenas zeros são aceitas: `"2.3500"`
equivale a `"2.35"`. Quantidade zero, negativa, não numérica, infinita,
`NaN` ou com precisão maior que a suportada retorna `422`.

O corpo recusa campos extras, inclusive `usuario_id`, `saldo`, `saldo_atual`,
`id`, `criado_em`, `estorno_de` e `motivo`. O autor é sempre obtido do cookie
do usuário autenticado. A unidade é a do item cadastrado e não é enviada no
corpo. `estorno` não é aceito por esta rota nesta entrega.

Resposta `201 Created`, partindo de um item com saldo zero:

```json
{
  "id": 31,
  "item_id": 12,
  "tipo": "entrada",
  "quantidade": "10.50",
  "observacao": "Doação recebida",
  "usuario_id": 7,
  "criado_em": "2026-10-31T18:00:00Z",
  "saldo_atual": "10.50"
}
```

Para registrar uma saída desse item:

```javascript
const resposta = await fetch("/movimentacoes", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    item_id: 12,
    tipo: "saida",
    quantidade: "2.25",
    observacao: "Entrega de alimentos",
  }),
});
const dados = await resposta.json();
```

Em caso de sucesso, essa saída retorna `201`, `tipo: "saida"`,
`quantidade: "2.25"` e `saldo_atual: "8.25"`. `quantidade` e `saldo_atual`
sempre são **strings decimais com duas casas**, inclusive quando a quantidade
foi enviada como número. Quantidade de saída continua positiva no histórico;
o campo `tipo` determina a subtração.

`saldo_atual` representa o saldo após essa movimentação. Outra movimentação
pode alterá-lo antes de o frontend receber a resposta; `GET /itens` fornece
o saldo atualizado para uma nova consulta. Não há paginação neste `POST`.

### Consistência do saldo

O backend bloqueia a linha do item com `SELECT ... FOR UPDATE`, confere o
saldo sob esse bloqueio e grava a atualização e o histórico na mesma
transação. Operações concorrentes do mesmo item aguardam a liberação da
linha e recalculam o saldo antes de prosseguir. Uma saída pode consumir todo
o saldo, mas não pode torná-lo negativo. Uma entrada não pode exceder
`99999999.99`, limite do `NUMERIC(10,2)` existente.

O backend executa rollback nas rejeições e falhas detectadas; saldo e histórico
pertencem à mesma transação. A implementação
segue o bloqueio de linhas descrito na
[documentação do PostgreSQL 16](https://www.postgresql.org/docs/16/explicit-locking.html#LOCKING-ROWS).
Não foi necessário alterar o schema do banco.

### Erros da movimentação

| Status | Condição | Corpo |
| --- | --- | --- |
| `401` | Ausência de autenticação válida ou usuário inativo. | `{"detail": "Não autenticado"}` |
| `404` | Item não existe. | `{"detail": "Item não encontrado."}` |
| `409` | Item inativo. | `{"detail": "Item inativo."}` |
| `409` | Saída maior que o saldo disponível. | `{"detail": "Saldo insuficiente para a saída."}` |
| `409` | Entrada faria o saldo ultrapassar o limite. | `{"detail": "Saldo máximo do item excedido."}` |
| `422` | Campos obrigatórios ausentes, extras, tipo ou quantidade inválidos. | `{"detail": [...]}`, no formato de validação já mostrado para itens. |

Requisições rejeitadas não alteram o saldo nem acrescentam histórico.
Falhas inesperadas do banco retornam erro de servidor, sem confirmar uma
movimentação parcial. Cada `POST` bem-sucedido cria uma nova movimentação;
esta entrega não oferece chave de idempotência para reenvios.

## Códigos de resposta

| Rota | Sucesso | Erros previstos |
| --- | --- | --- |
| `POST /auth/login` | `200` | `401` credenciais/usuário; `422` validação; `429` limite de tentativas. |
| `POST /itens` | `201` | `401` autenticação; `409` par nome/unidade duplicado; `422` validação. |
| `GET /itens` | `200` | `401` autenticação; `422` paginação inválida. |
| `POST /movimentacoes` | `201` | `401` autenticação; `404` item; `409` conflito de estoque; `422` validação. |

## Verificação

Os testes de integração em `backend/tests/test_itens.py` usam PostgreSQL
real, login por `/auth/login` e o cookie recebido. Apenas a conexão de banco
é direcionada para um schema isolado; a autenticação não é substituída.
Comandos, resultados e limites da verificação estão em [testes.md](testes.md).

Os testes em `test_movimentacoes.py` e `test_movimentacoes_concorrencia.py`
também verificam entrada, saída, rollback e requisições concorrentes contra
o PostgreSQL, usando o mesmo login real e autenticação por cookie.
