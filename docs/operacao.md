# Publicação do site institucional na Cloudflare

## Destinos da aplicação

| Componente | Destino | Diretório no repositório |
| --- | --- | --- |
| Site institucional estático | Cloudflare Workers Static Assets | `site/` |
| Painel de estoque | VM | `estoque/` |
| API Python/FastAPI | VM | `backend/` |
| PostgreSQL | VM | Configuração privada do backend |

O Worker `trabalho-web-iii` publica somente os arquivos de `site/`.
Não é necessário iniciar Python, instalar `backend/requirements.txt` ou
conectar PostgreSQL para publicar esse site.

## Configuração esperada no painel

Em **Workers & Pages > trabalho-web-iii > Settings > Build**, conferir com
o responsável pela conta:

| Configuração | Valor esperado para este repositório |
| --- | --- |
| Root directory | `site` |
| Build command | Vazio: HTML, CSS, JavaScript e imagens já são arquivos estáticos. |
| Deploy command | `npx wrangler deploy --config wrangler.jsonc` |
| Production branch | `main` |
| Preview/non-production command, se habilitado | `npx wrangler versions upload --config wrangler.jsonc` |

`versions upload` cria uma versão para verificação sem promover a branch de
desenvolvimento à produção. O PR deve continuar aberto para revisão e merge
pelo João. Os comandos de produção dependem das permissões e autenticação
do projeto na Cloudflare.

Esses são valores esperados, **não configurações lidas ou alteradas nesta
investigação**: não houve acesso autenticado ao painel. Se for mantida a raiz
do repositório como pasta de execução, o comando equivalente deve especificar
`--config site/wrangler.jsonc`; não usar `--config site/wrangler.jsonc`
quando a pasta de execução já for `site/`.

O arquivo `site/wrangler.jsonc` define `assets.directory` como `.`. O Wrangler
resolve esse caminho em relação à pasta da configuração: o resultado é
`site/`, e não a raiz do repositório. `site/.assetsignore` exclui a configuração
e os artefatos locais do conjunto de arquivos servidos. Os diretórios
`.wrangler/` também são ignorados pelo Git.

Referências oficiais: [configuração de Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/)
e [assets e exclusões](https://developers.cloudflare.com/workers/static-assets/binding/).

## Caminhos publicados

| Arquivo local | URL verificada localmente |
| --- | --- |
| `site/index.html` | `/` |
| `site/como-ajudar.html` | `/como-ajudar` |
| `site/contato.html` | `/contato` |
| `site/nossas-acoes.html` | `/nossas-acoes` |
| `site/quem-somos.html` | `/quem-somos` |
| `site/static/style.css` | `/static/style.css` |
| `site/static/index.js` | `/static/index.js` |
| `site/static/img.png` | `/static/img.png` |

Não há prefixo `/site` na URL pública. O caminho antigo
`/templates/cadastro` não corresponde a um arquivo do site institucional;
o painel de estoque pertence à VM.

## Diagnóstico e validação local em 31/10/2026

A checagem `Workers Builds: trabalho-web-iii` do commit `14f4d46`, no
[PR #1](https://github.com/RAZIEL-SEC/Trabalho-Web-III/pull/1), informou falha
no build `9f83e1a3-e06b-435e-9e8d-f9d51c28ffdd`. A API do GitHub forneceu
somente um link para a Cloudflare: sem texto de log, sem anotações e sem
execução correspondente no GitHub Actions. O usuário também informou que
o link retornou “Page not found” ou falta de permissão. **O comando, a pasta
de execução, a mensagem de erro e a causa dessa falha remota permanecem não
confirmados**, até obter os logs e a configuração do painel com João.

Foi confirmado separadamente um erro no repositório: `assets.directory`
apontava para `./frontend`, resolvido como `site/frontend`, que não existe.
Com Node.js `24.22.2` e Wrangler `4.148.0`, o comando local, na raiz, foi:

```powershell
npx --yes wrangler@4.148.0 deploy --config site/wrangler.jsonc --dry-run --outdir .pytest_cache/wrangler-before
```

Resultado anterior à correção: código de saída `1`, com a mensagem:

```text
The directory specified by the "assets.directory" field in your configuration file does not exist:
<repositorio>/site/frontend
```

Depois da correção para `.`, o mesmo dry-run, usando
`--outdir .pytest_cache/wrangler-after`, terminou com código `0` e
`--dry-run: exiting now.`. Também passou o comando equivalente a partir
de `site/`:

```powershell
npx --yes wrangler@4.148.0 deploy --config wrangler.jsonc --dry-run
```

O segundo comando foi executado pelo binário local do mesmo Wrangler já
instalado em cache, com a opção `--outdir` apontando para o cache na raiz.
Nenhum desses comandos realizou deploy. Node e Wrangler foram usados de forma
portátil no cache ignorado, sem adicionar dependências ao repositório.

O comando de preview documentado também foi validado a partir de `site/`,
pelo mesmo binário em cache, com código de saída `0`:

```powershell
npx --yes wrangler@4.148.0 versions upload --config wrangler.jsonc --dry-run
```

Foi usado um `--outdir` no cache da raiz; nenhuma versão foi enviada nesse teste.

Também foi iniciado temporariamente `wrangler dev --local`, em
`127.0.0.1:18787`, com a configuração de `site/`. Um script Python via entrada
padrão consultou 16 URLs HTTP: as oito públicas acima retornaram `200`, e
`/wrangler.jsonc`, `/.assetsignore`, `/backend/app/main.py`,
`/estoque/login.html`, `/.env`, `/backend/.env`, `/database/schema.sql` e
`/templates/cadastro` retornaram `404`. O servidor local foi encerrado após
a conferência.

Os arquivos HTML, CSS, JavaScript e imagem do site atualmente são placeholders
vazios. As verificações confirmam configuração, roteamento e exclusões;
não validam conteúdo visual ou integração das telas. Não foi repetida a suíte
do backend, pois nenhuma funcionalidade Python foi alterada nesta correção.
Um dry-run local bem-sucedido não comprova o sucesso da execução remota:
essa confirmação depende da nova checagem do PR e do acesso aos logs.
