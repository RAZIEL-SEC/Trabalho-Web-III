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

## Configuração aplicada na Cloudflare

A configuração do Worker `trabalho-web-iii` foi consultada e corrigida pela
API da Cloudflare em 05/11/2026. Em **Workers & Pages > trabalho-web-iii >
Settings > Builds**, os valores ativos são:

| Configuração | Valor esperado para este repositório |
| --- | --- |
| Root directory | `site` |
| Build command | Vazio: HTML, CSS, JavaScript e imagens já são arquivos estáticos. |
| Deploy command | `npx wrangler deploy --config wrangler.jsonc` |
| Production branch | `main` |
| Preview/non-production command, se habilitado | `npx wrangler preview --config wrangler.jsonc` |

`wrangler preview` cria/atualiza um preview isolado para a branch ou PR, sem
promover essa versão à produção. O PR deve continuar aberto para revisão e
merge. Os comandos de produção dependem das permissões e autenticação do
projeto na Cloudflare.

As configurações de preview também foram propagadas aos ambientes de preview já existentes, para que cada branch use a raiz `site/` e o comando `npx wrangler preview --config wrangler.jsonc`.

O problema de sincronização era que o Worker estava configurado para observar
a branch `front-end`, enquanto a aplicação e o deploy da VPS usam `main`.
Além disso, a raiz de build estava como `/`, embora o arquivo Wrangler esteja
em `site/wrangler.jsonc`. A configuração foi alinhada para `main` e `site`;
os comandos usam o arquivo `wrangler.jsonc` a partir dessa raiz.

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

## Histórico do diagnóstico de Cloudflare (31/10/2026)

A API da Cloudflare permitiu recuperar os logs dos builds que falharam em
23/10/2026. Um deles executou `npx wrangler deploy`, leu assets de
`/opt/buildhome/repo/frontend` e falhou com o erro `100324`: configuração
`_redirects` inválida, com loop infinito ao remover `.html` ou `/index`.
Isso explica a falha antiga; a publicação atual foi separada para a pasta
`site/`, que não contém aquela regra de redirecionamento.

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

O comando `versions upload` também passou em dry-run local, mas não é o comando
de preview usado pelo Workers Builds. Para PRs e branches, a configuração ativa
usa `npx wrangler preview --config wrangler.jsonc`, conforme a documentação do
Cloudflare Workers Builds.

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


## Sincronização automática e deploy da VPS (05/11/2026)

A configuração da Cloudflare mostrava a branch de produção `front-end`, não
`main`. A raiz de build era `/`, apesar de a configuração Wrangler estar em
`site/wrangler.jsonc`. Foi corrigido na conta do Worker para:
- branch de produção: `main`;
- raiz: `site`;
- deploy: `npx wrangler deploy --config wrangler.jsonc`;
- preview: `npx wrangler preview --config wrangler.jsonc`.

A execução mais recente do deploy da VPS falhou depois de iniciar os containers,
não durante o SSH nem durante o build Docker. O comando de health check foi
executado imediatamente após iniciar o container e recebeu `curl: (52) Empty
reply from server`. O workflow agora aguarda a API por até 60 segundos,
mostra os logs se ela não ficar saudável e só então limpa imagens antigas.
Também atualiza apenas o serviço `app`, sem recriar o PostgreSQL.

O workflow passou a executar a suíte `pytest` em um PostgreSQL temporário
antes do deploy. Em Pull Requests, executa os testes sem publicar na VPS.
