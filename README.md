# Amigos do Zé Alguém

Projeto desenvolvido na disciplina de Web III para apoiar a ONG Amigos do Zé
Alguém na divulgação de suas ações e no controle de doações e estoque.

O projeto tem dois componentes, mantidos em branches diferentes:

| Componente | Código | Tecnologias | Publicação |
| --- | --- | --- | --- |
| Site institucional | Branch [front-end](https://github.com/RAZIEL-SEC/Trabalho-Web-III/tree/front-end), com `src/` e `public/` na raiz | React, TypeScript, Tailwind CSS e Vite | Cloudflare Workers Static Assets |
| Sistema de estoque | Branch [main](https://github.com/RAZIEL-SEC/Trabalho-Web-III/tree/main): painel em `estoque/`, API em `backend/` e SQL em `database/` | HTML, CSS e JavaScript puro no painel; Python com FastAPI na API; PostgreSQL no banco | VPS, com Docker Compose e proxy reverso HTTPS |

## Acessos

- [Site institucional](https://trabalho-web-iii.razielsec01.workers.dev/)
- [Painel de estoque](https://amigosdozealguem.duckdns.org/estoque/login)

## Funcionalidades do estoque

- Cadastro e listagem paginada de itens com grupo e subgrupo gerenciáveis pelo painel, além de unidades de medida variadas: peso, volume e embalagens/contagens (kg, g, un, l, ml, pacote, garrafa, frasco, lata, caixa, fardo, kit, par, rolo, dúzia, bandeja, saco e galão).
- Gerenciamento de grupos e subgrupos, com criação, renomeação, desativação protegida por dependências e filtros de classificação no cadastro/listagem de itens. Itens existentes recebem a classificação padrão “Sem classificação” durante a migração.\n- Entradas e saídas com atualização transacional do saldo, proteção contra saldo
  negativo e chave de idempotência para evitar movimentações duplicadas por reenvio.
- Consulta de saldos e histórico paginado de movimentações.
- Autenticação por cookie de sessão, troca de senha e encerramento de sessões.
- Perfil **operador** para as operações de estoque e perfil **admin** com acesso
  adicional à administração de usuários, perfis e senhas.
- Registro de ações de segurança e administração em auditoria.

## Executar o estoque localmente

Este fluxo usa Python no ambiente virtual e PostgreSQL instalado localmente.
A configuração do Docker Compose da VPS está em uma seção separada abaixo.

### 1. Pré-requisitos e código

Instale Git, Python 3.12 ou 3.13 e PostgreSQL 16. Mantenha o serviço PostgreSQL
ativo e disponibilize `psql`, `createuser` e `createdb` no `PATH` do terminal.

Em PowerShell ou Linux/macOS:

```shell
git clone --branch main https://github.com/RAZIEL-SEC/Trabalho-Web-III.git
cd Trabalho-Web-III
```

Se já tiver o repositório, use sua cópia existente. Os próximos passos partem
da raiz do projeto; não sobrescreva uma configuração local já preenchida.

### 2. Ambiente virtual e dependências

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
if (-not (Test-Path backend/.env)) { Copy-Item .env.example backend/.env }
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
test -f backend/.env || cp .env.example backend/.env
```

### 3. Configuração do backend

Edite `backend/.env` para usar o banco e as credenciais locais. Exemplo de
estrutura, substituindo os valores entre `<...>`:

```dotenv
DATABASE_URL=postgresql+psycopg://estoque:<senha-local>@127.0.0.1:5432/estoque
SECRET_KEY=<chave-aleatoria-gerada>
ACCESS_TOKEN_MINUTES=15
APP_ENV=development
COOKIE_SECURE=false
```

Gere uma chave privada com o ambiente virtual ativo, em qualquer um dos terminais:

```shell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Use a mesma senha definida para o usuário PostgreSQL `estoque`. Se ela tiver
caracteres reservados de URL, codifique-os na `DATABASE_URL`.

Ao copiar o `.env.example` atual, **remova `FORWARDED_ALLOW_IPS` do
`backend/.env`**. Essa variável configura o Uvicorn na VPS e não é um campo
aceito por `Settings` do backend; variáveis extras nesse arquivo causam erro
de validação. Nunca versione `.env`, senhas, chaves ou cookies.

### 4. Criar o banco e aplicar o esquema inicial

Para uma instalação nova, execute os comandos abaixo a partir da raiz do
repositório. Eles funcionam no PowerShell e no Linux/macOS. Use uma conta
administradora do PostgreSQL; ajuste `-U postgres` se ela tiver outro nome.

```shell
createuser -h 127.0.0.1 -U postgres --login --pwprompt estoque
createdb -h 127.0.0.1 -U postgres --owner=estoque estoque
psql -h 127.0.0.1 -U estoque -d estoque -v ON_ERROR_STOP=1 -f database/schema.sql
```

O primeiro comando solicita a senha do novo usuário. O esquema deve ser
aplicado como `estoque`, proprietário do banco. Se o usuário e o banco já
existirem, preserve-os e use suas credenciais. **Não reaplique `schema.sql`
em um banco já inicializado**: ele cria tabelas e não é um script de atualização.

### 5. Aplicar as migrações

Com o ambiente virtual ativo, execute em ambos os sistemas:

```shell
cd backend
python -m app.migrate
cd ..
```

O comando lê `backend/.env` e executa os arquivos SQL de
`database/migrations/` em ordem de nome. As migrações atuais permitem
reexecução, mas pressupõem a existência das tabelas do esquema inicial.
Em um banco existente, faça backup antes de aplicar atualizações.

### 6. Criar o primeiro administrador

Na raiz do repositório, em PowerShell ou Linux/macOS:

```shell
python scripts/criar_usuario.py --nome "Administrador" --email admin@example.org --admin
```

Troque o nome e o e-mail pelos dados do responsável. O script solicita e
confirma a senha de forma interativa, com mínimo de 10 caracteres, e carrega
a configuração de `backend/.env`. Depois, um administrador pode cadastrar
os demais usuários pelo painel; não há cadastro público de contas.

### 7. Iniciar a API e abrir o painel

Com o ambiente virtual ativo, em ambos os sistemas:

```shell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Painel local: <http://127.0.0.1:8000/estoque/login>
- Documentação interativa da API: <http://127.0.0.1:8000/docs>
- Saúde da API e conexão com o banco: <http://127.0.0.1:8000/saude>

Com a conexão funcionando, `GET /saude` deve retornar `200` com
`{"status":"ok"}`. A própria API serve os arquivos de `estoque/`, mantendo
painel e API na mesma origem; não é necessário um servidor separado para o painel.

## Docker Compose na VPS

O `docker-compose.yml` da raiz descreve a implantação do estoque na VPS, com
PostgreSQL 16 e a API. Ele exige um **`.env` na raiz**, distinto do
`backend/.env` usado no desenvolvimento local:

```dotenv
DB_PASSWORD=<senha-forte-do-banco-compativel-com-URL>
SECRET_KEY=<chave-privada-com-pelo-menos-32-caracteres>
FORWARDED_ALLOW_IPS=<IP-ou-CIDR-restrito-do-proxy>
```

O Compose monta a `DATABASE_URL` com o host interno `db` e define
`APP_ENV=production`, `COOKIE_SECURE=true` e sessões de 15 minutos.
Preserve as credenciais de volumes existentes: alterar `DB_PASSWORD` no
arquivo não altera a senha de um banco já criado.

Para a primeira inicialização, na raiz do repositório na VPS:

```shell
docker compose up -d --build
```

O PostgreSQL aplica `database/schema.sql` somente quando inicializa um volume
`pgdata` vazio. Antes de iniciar o Uvicorn, o container da API executa
`python -m app.migrate`, inclusive nas atualizações de bancos persistentes.

Para criar o primeiro administrador nessa instalação, use o script com o banco
e as variáveis do Compose. Como `scripts/` não é copiado para a imagem, monte-o
temporariamente no comando abaixo, executado na raiz do repositório na VPS:

```shell
docker compose run --rm --no-deps --volume ./scripts:/srv/scripts:ro app python /srv/scripts/criar_usuario.py --nome "Administrador" --email admin@example.org --admin
```

O workflow em [deploy.yml](.github/workflows/deploy.yml) executa testes antes
da publicação. Nos PRs para `main`, somente os testes são executados; no push
para `main`, a aplicação também é atualizada na VPS.

### Proxy HTTPS, sessão e CSRF

A API fica vinculada a `127.0.0.1:8000` na VPS e deve ser acessada externamente
pelo proxy reverso HTTPS. O proxy deve sobrescrever `X-Forwarded-For` e
encaminhar `X-Forwarded-Proto`. Configure `FORWARDED_ALLOW_IPS` com os IPs
ou CIDRs restritos do proxy que realmente se conecta ao Uvicorn, separados
por vírgulas. O fallback do Compose é `127.0.0.1`; não use `*` nem reutilize
automaticamente o endereço de outra infraestrutura. Restrinja também o
acesso por firewall/regras de rede.

O cookie de sessão usa `HttpOnly` e `SameSite=Strict`, com `Secure` obrigatório
em produção. Requisições que alteram estado exigem `Origin` ou `Referer`
válido. Nas operações autenticadas, exceto no login, também é necessário
enviar `X-CSRF-Token`, obtido em `GET /auth/csrf`. O JavaScript do painel
faz essa obtenção automaticamente.

Por padrão, a API aceita a própria origem. `CSRF_TRUSTED_ORIGINS`, opcional
no `.env` da VPS, permite origens HTTPS exatas separadas por vírgulas, mas
**não habilita CORS nem compartilhamento de cookies entre sites**. Mantenha
painel e API na mesma origem; outra arquitetura exige revisar CORS com
credenciais e a política de cookies em conjunto.

## Site institucional: branch front-end

O institucional é mantido na branch `front-end`, separadamente do estoque.
Nessa branch, `package.json` declara `dev` como `vite`, `build` como
`vite build` e `preview` como `vite preview`. O `.mise.toml` seleciona Node.js
22; use Node 22.12 ou superior da série 22, conforme o requisito do Vite no lockfile.

Em um checkout separado, os comandos são os mesmos nos dois sistemas:

```shell
git clone --branch front-end --single-branch https://github.com/RAZIEL-SEC/Trabalho-Web-III.git Amigos-do-Ze-Alguem-site
cd Amigos-do-Ze-Alguem-site
npm ci
npm run dev
```

Para gerar e conferir o build localmente:

```shell
npm run build
npm run preview
```

O Vite gera `dist/`. O `wrangler.jsonc` dessa branch define o Worker
`trabalho-web-iii`, com `assets.directory: "./dist"` e tratamento de rotas
como aplicação de página única (`single-page-application`).

Para configurar a publicação no Cloudflare Workers Builds, use o código
da branch `front-end` e estes valores, após instalar as dependências:

| Configuração | Valor |
| --- | --- |
| Branch de produção | `front-end` |
| Diretório raiz | Raiz da branch (`/`) |
| Comando de build | `npm run build` |
| Comando de deploy | `npx wrangler deploy` |
| Diretório dos assets, definido no Wrangler | `./dist` |

O deploy requer autenticação e permissões na conta da Cloudflare. Ele publica
somente o institucional; painel, API e PostgreSQL permanecem na VPS.

## Documentação

- [Contrato da API](docs/contrato-api.md): autenticação, requisições,
  respostas, validações e representação dos valores decimais.
- [Guia de testes](docs/testes.md): comandos, isolamento do PostgreSQL e
  resultados registrados nas entregas.
