# Trabalho-Web-III
Projeto desenvolvido na disciplina de Web 3, com o objetivo de criar um sistema web completo para uma ONG sem fins lucrativos. A aplicação conta com um site integrado a um banco de dados, permitindo o gerenciamento e a organização das informações da instituição de forma simples, segura e eficiente.

git clone https://github.com/RAZIEL-SEC/Trabalho-Web-III.git
cd Trabalho-Web-III

python3 -m venv .venv
source .venv/bin/activate          // Windows: .venv\\Scripts\\activate
python -m pip install -r backend/requirements.txt

// Linux: cp .env.example backend/.env

// Windows: copy .env.example backend\\.env
docker compose up -d
cd backend
uvicorn app.main:app --reload


https://trabalho-web-iii.razielsec01.workers.dev

https://amigosdozealguem.duckdns.org/estoque/login.html


## Migrações do banco

Ao iniciar o container da API, o comando `python -m app.migrate` aplica os
scripts SQL idempotentes de `database/migrations/` antes de iniciar o Uvicorn.
Isso permite atualizar bancos persistentes já existentes sem depender da
execução de `schema.sql`, que o PostgreSQL executa apenas na criação inicial
do volume.

A API deve ficar acessível somente pelo proxy reverso. O proxy deve sobrescrever
`X-Forwarded-For`; o backend usa o primeiro endereço válido desse cabeçalho
para aplicar o limite por IP. Não exponha a porta da API diretamente à internet.
Em produção, configure `APP_ENV=production` e `COOKIE_SECURE=true`.

### Proxy reverso e cabeçalhos encaminhados

O Uvicorn só deve confiar nos cabeçalhos `X-Forwarded-Proto` e
`X-Forwarded-For` quando a conexão vier de um proxy conhecido. A lista é
configurada pela variável `FORWARDED_ALLOW_IPS`, que aceita IPs ou CIDRs
separados por vírgula. O Compose usa `127.0.0.1` como fallback conservador;
em uma implantação atrás de proxy, configure explicitamente o endereço ou a
faixa privada restrita do proxy no arquivo `.env`.

Exemplo para a VPS atual, após confirmar o endereço de origem do Caddy na rede
Docker:

```env
FORWARDED_ALLOW_IPS=172.20.0.1
```

Não use `*` como configuração padrão. Mantenha a porta da API acessível
somente pelo proxy e limite o tráfego por firewall/regras de rede. Em outra
infraestrutura, como AWS, configure o IP privado ou CIDR específico do proxy
real daquela arquitetura; não reutilize automaticamente o endereço da VPS.
Se o proxy tiver endereços dinâmicos, restrinja também o acesso por Security
Groups/firewall e escolha uma faixa privada dedicada ao proxy.

O Dockerfile habilita explicitamente `--proxy-headers` e passa a lista
`FORWARDED_ALLOW_IPS` ao Uvicorn. Isso permite que o FastAPI reconheça o
esquema HTTPS original encaminhado pelo Caddy sem ampliar a confiança a
origens não autorizadas.

## Proteção CSRF

As requisições que alteram estado exigem uma origem válida em `Origin` ou,
na ausência desse cabeçalho, em `Referer`. Para sessões autenticadas, também
é obrigatório enviar o cabeçalho `X-CSRF-Token`, obtido em `GET /auth/csrf`.
O frontend do painel já faz essa obtenção automaticamente.

Por padrão, somente a mesma origem da API é aceita. `CSRF_TRUSTED_ORIGINS`
é apenas uma allowlist para a validação de origem; ela **não habilita CORS**
nem faz o navegador enviar cookies entre origens. Se painel e API realmente
estiverem em origens diferentes, será necessário projetar CORS com credenciais,
`fetch(..., { credentials: "include" })` e a política de cookies em conjunto.
Prefira manter painel e API na mesma origem. Quando necessário, configure
origens HTTPS exatas (incluindo porta), separadas por vírgulas, sem curingas.



**Importante:** a allowlist de CSRF não altera a política do cookie de sessão
(`SameSite=Strict`). Uma origem em outro subdomínio do mesmo site pode ser
autorizada após validação, mas um frontend em outro site/domínio não passará a
compartilhar a sessão apenas por entrar na allowlist. Nesse cenário, prefira
servir painel e API sob a mesma origem (ou ao menos o mesmo site); não altere
`SameSite` para `None` sem projetar também CORS com credenciais e revisar o
modelo de cookies.
