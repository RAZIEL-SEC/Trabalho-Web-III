# Trabalho-Web-III

Projeto desenvolvido na disciplina de Web 3, com o objetivo de criar um sistema web completo para uma ONG sem fins lucrativos. A aplicação conta com um site integrado a um banco de dados, permitindo o gerenciamento e a organização das informações da instituição de forma simples, segura e eficiente.

## Execução do projeto

```bash
git clone https://github.com/RAZIEL-SEC/Trabalho-Web-III.git
cd Trabalho-Web-III

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt

# Linux
cp .env.example backend/.env

# Windows
# copy .env.example backend\.env

docker compose up -d
cd backend
uvicorn app.main:app --reload
```

Ambientes publicados:

- Site: https://trabalho-web-iii.razielsec01.workers.dev
- Painel: https://amigosdozealguem.duckdns.org/estoque/login.html

## Migrações do banco

Ao iniciar o container da API, o comando `python -m app.migrate` aplica os scripts SQL idempotentes de `database/migrations/` antes de iniciar o Uvicorn. Isso permite atualizar bancos persistentes já existentes sem depender da execução de `schema.sql`, que o PostgreSQL executa apenas na criação inicial do volume.

A API deve ficar acessível somente pelo proxy reverso. O proxy deve sobrescrever `X-Forwarded-For`; o backend usa o primeiro endereço válido desse cabeçalho para aplicar o limite por IP. Não exponha a porta da API diretamente à internet. Em produção, configure `APP_ENV=production` e `COOKIE_SECURE=true`.

### Proxy reverso e cabeçalhos encaminhados

O Uvicorn só deve confiar nos cabeçalhos `X-Forwarded-Proto` e `X-Forwarded-For` quando a conexão vier de um proxy conhecido. A lista é configurada pela variável `FORWARDED_ALLOW_IPS`, que aceita IPs ou CIDRs separados por vírgula. O Compose usa `127.0.0.1` como fallback conservador; em uma implantação atrás de proxy, configure explicitamente o endereço ou a faixa privada restrita do proxy no arquivo `.env`.

Exemplo para a VPS atual, após confirmar o endereço de origem do Caddy na rede Docker:

```env
FORWARDED_ALLOW_IPS=172.20.0.1
```

Não use `*` como configuração padrão. Mantenha a porta da API acessível somente pelo proxy e limite o tráfego por firewall/regras de rede. Em outra infraestrutura, como AWS, configure o IP privado ou CIDR específico do proxy real daquela arquitetura; não reutilize automaticamente o endereço da VPS. Se o proxy tiver endereços dinâmicos, restrinja também o acesso por Security Groups/firewall e escolha uma faixa privada dedicada ao proxy.

O Dockerfile habilita explicitamente `--proxy-headers` e passa a lista `FORWARDED_ALLOW_IPS` ao Uvicorn. Isso permite que o FastAPI reconheça o esquema HTTPS original encaminhado pelo Caddy sem ampliar a confiança a origens não autorizadas.

## Proteção CSRF

As requisições que alteram estado exigem uma origem válida em `Origin` ou, na ausência desse cabeçalho, em `Referer`. Para sessões autenticadas, também é obrigatório enviar o cabeçalho `X-CSRF-Token`, obtido em `GET /auth/csrf`. O frontend do painel já faz essa obtenção automaticamente.

Por padrão, somente a mesma origem da API é aceita. `CSRF_TRUSTED_ORIGINS` é apenas uma allowlist para a validação de origem; ela **não habilita CORS** nem faz o navegador enviar cookies entre origens. Se painel e API realmente estiverem em origens diferentes, será necessário projetar CORS com credenciais, `fetch(..., { credentials: "include" })` e a política de cookies em conjunto. Prefira manter painel e API na mesma origem. Quando necessário, configure origens HTTPS exatas (incluindo porta), separadas por vírgulas, sem curingas.

**Importante:** a allowlist de CSRF não altera a política do cookie de sessão (`SameSite=Strict`). Uma origem em outro subdomínio do mesmo site pode ser autorizada após validação, mas um frontend em outro site/domínio não passará a compartilhar a sessão apenas por entrar na allowlist. Nesse cenário, prefira servir painel e API sob a mesma origem (ou ao menos o mesmo site); não altere `SameSite` para `None` sem projetar também CORS com credenciais e revisar o modelo de cookies.

---

# Sistema de backup e recuperação

O projeto inclui um gerenciador de backup que empacota os arquivos do sistema e um dump do PostgreSQL, criptografa o pacote e o envia a um chat privado do Telegram. Também oferece dois modos de restauração: projeto completo ou somente banco de dados.

> **Situação operacional:** o primeiro backup manual foi enviado e confirmado pelo Telegram. A ativação do timer do systemd e um teste de restauração isolado ainda precisam ser verificados na VPS. Não considere o agendamento diário ativo até confirmar `systemctl list-timers`.

## 1. O que é incluído

Cada backup contém:

- Arquivos do projeto, incluindo o arquivo `.env` existente na raiz do projeto.
- Exportação do PostgreSQL em formato customizado, gerada por `pg_dump -Fc`.
- Um `manifest.json` com informações sobre o formato e o conteúdo do pacote.

O backup **não** inclui:

- Histórico e metadados do Git (`.git`).
- Ambientes virtuais Python (`.venv` e `.venv-backup`).
- Cache, arquivos compilados, `node_modules`, `.wrangler` e diretórios locais de backup.
- Serviços e configurações externos à pasta do projeto, como Caddy, certificados TLS, firewall, regras de rede e configurações da própria VPS.

Arquivos `.env` são incluídos intencionalmente no pacote, mas ficam protegidos pela criptografia do backup. Nunca envie o arquivo de configuração de credenciais do backup para o repositório.

## 2. Criptografia e integridade

O arquivo compactado é criptografado com:

- **AES-256-GCM**, que oferece confidencialidade e autenticação dos dados.
- **Argon2id**, usado para derivar a chave a partir da senha do backup, com salt aleatório por arquivo.
- **SHA-256**, calculado sobre o arquivo criptografado. O hash é incluído na legenda enviada ao Telegram e deve ser guardado junto do backup.

A senha não é armazenada no arquivo de backup. Sem a senha correta, o conteúdo não pode ser descriptografado. Uma senha incorreta ou alteração do arquivo causa falha na verificação de autenticação do AES-GCM.

Arquivos criptografados maiores que 40 MiB são divididos em partes numeradas (`.part0001`, `.part0002` etc.). Todas as partes devem ser baixadas para a mesma pasta. Na restauração, o gerenciador as reúne em ordem e valida o SHA-256 antes de descriptografar.

**Guarde a senha do backup em um gerenciador de senhas ou em outro local seguro.** O Telegram armazena o arquivo criptografado, mas não substitui uma cópia segura da senha. Se a senha for perdida, o backup não poderá ser recuperado.

## 3. Requisitos na VPS

A instalação descrita abaixo considera Ubuntu, o usuário de serviço `ubuntu`, Docker Compose e o projeto em:

```text
/home/ubuntu/Trabalho-Web-III
```

O servidor precisa ter:

- Docker Engine e Docker Compose plugin instalados.
- Usuário de execução com permissão para usar Docker (grupo `docker`).
- Python 3.8 ou superior compatível com as dependências do arquivo `scripts/requirements-backup.txt`.
- Acesso HTTPS de saída para `api.telegram.org`.
- Bot do Telegram criado no BotFather e uma conversa privada iniciada com ele.

## 4. Configurar as credenciais

Crie o arquivo de ambiente fora do repositório:

```bash
sudo install -m 600 /dev/null /etc/trabalho-web-iii-backup.env
sudo chown root:ubuntu /etc/trabalho-web-iii-backup.env
sudo chmod 640 /etc/trabalho-web-iii-backup.env
sudoedit /etc/trabalho-web-iii-backup.env
```

Preencha com as três variáveis abaixo, usando os valores reais do seu bot e uma senha forte e exclusiva:

```dotenv
TELEGRAM_BOT_TOKEN=TOKEN_DO_BOT
TELEGRAM_CHAT_ID=ID_DO_CHAT_PRIVADO
BACKUP_PASSPHRASE=SENHA_FORTE_E_EXCLUSIVA
```

A senha deve ter pelo menos 16 caracteres. Recomenda-se gerar uma senha aleatória longa, por exemplo com `openssl rand -hex 32`, e armazená-la também em um gerenciador de senhas.

O arquivo fica com permissão `640`, proprietário `root` e grupo `ubuntu`: o systemd consegue ler o arquivo e o script executado por `ubuntu` consegue carregá-lo. Não coloque esses valores no Git, em mensagens públicas, no README ou em logs.

## 5. Instalar as dependências

Na pasta do projeto:

```bash
cd /home/ubuntu/Trabalho-Web-III

sudo apt update
sudo apt install -y python3-venv

python3 -m venv .venv-backup
.venv-backup/bin/python -m pip install --upgrade pip
.venv-backup/bin/python -m pip install -r scripts/requirements-backup.txt

chmod 750 scripts/backup.sh scripts/restore.sh
chmod 640 scripts/backup_manager.py scripts/requirements-backup.txt
```

O ambiente `.venv-backup` é separado do ambiente Python da aplicação. Ele não deve ser commitado.

## 6. Executar um backup manual

Com Docker Compose em execução e as credenciais configuradas:

```bash
cd /home/ubuntu/Trabalho-Web-III
./scripts/backup.sh
```

O comando:

1. Verifica a senha e as credenciais do Telegram.
2. Executa `pg_dump` dentro do serviço `db` do Docker Compose.
3. Empacota os arquivos do projeto e o dump do banco.
4. Criptografa o pacote.
5. Calcula o SHA-256 do arquivo criptografado.
6. Envia o arquivo ao Telegram, dividindo-o em partes de 40 MiB quando necessário.

Ao final, o terminal deve informar que o Telegram confirmou o recebimento. Confira também se o documento chegou ao chat do bot. Guarde o arquivo e a legenda com o SHA-256.

## 7. Agendamento diário com systemd

Os arquivos de unidade estão em `deploy/`:

- `trabalho-web-iii-backup.service`: executa o backup como usuário `ubuntu`, com acesso ao Docker.
- `trabalho-web-iii-backup.timer`: agenda a execução diária.

O timer usa o fuso horário local configurado no servidor. Confira-o antes de ativar:

```bash
timedatectl
```

Instale e habilite as unidades:

```bash
cd /home/ubuntu/Trabalho-Web-III

sudo install -m 644 deploy/trabalho-web-iii-backup.service /etc/systemd/system/
sudo install -m 644 deploy/trabalho-web-iii-backup.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now trabalho-web-iii-backup.timer
```

O agendamento está configurado para iniciar às **03:15**, com uma tolerância aleatória de até 5 minutos (`RandomizedDelaySec=5m`). `Persistent=true` permite que o systemd dispare uma execução perdida enquanto o servidor estava desligado, após o timer voltar a ser ativado.

Verifique o próximo disparo:

```bash
systemctl list-timers --all | grep trabalho-web-iii-backup
```

Consulte o estado e os logs:

```bash
sudo systemctl status trabalho-web-iii-backup.timer
sudo journalctl -u trabalho-web-iii-backup.service -n 100 --no-pager
```

Para executar imediatamente pelo systemd:

```bash
sudo systemctl start trabalho-web-iii-backup.service
```

Para desativar o agendamento:

```bash
sudo systemctl disable --now trabalho-web-iii-backup.timer
```

## 8. Como recuperar um backup

### 8.1. Preparar o arquivo

1. Abra o chat privado com o bot no Telegram.
2. Baixe o documento do backup e, se houver divisão, **todas** as partes.
3. Copie os arquivos para a mesma pasta na VPS.
4. Não renomeie as partes.
5. Copie o SHA-256 completo da legenda do Telegram.

Exemplo:

```bash
mkdir -p ~/backup-restore
chmod 700 ~/backup-restore
ls -lh ~/backup-restore
```

O arquivo único termina em `.tar.gz.enc`. Quando houver divisão, informe ao comando a primeira parte, terminada em `.part0001`. O programa localizará as demais partes na mesma pasta, reconstruirá o arquivo e validará o hash antes de descriptografar.

### 8.2. Disponibilizar a senha

A restauração solicita a senha de forma interativa se `BACKUP_PASSPHRASE` não estiver definida no ambiente. Para evitar colocá-la no histórico do shell:

```bash
read -rsp "Senha do backup: " BACKUP_PASSPHRASE
echo
export BACKUP_PASSPHRASE
```

Depois da restauração, remova a variável da sessão:

```bash
unset BACKUP_PASSPHRASE
```

### 8.3. Restaurar somente o banco de dados

> **Atenção:** este procedimento sobrescreve objetos e dados do banco atual. Faça um backup do estado atual antes de continuar e confirme que está usando o arquivo e o SHA-256 corretos.

```bash
cd /home/ubuntu/Trabalho-Web-III

./scripts/restore.sh \
  --input ~/backup-restore/NOME_DO_BACKUP.tar.gz.enc \
  --sha256 HASH_SHA256_COMPLETO \
  --mode database \
  --project-dir /home/ubuntu/Trabalho-Web-III \
  --confirm-overwrite
```

Se o backup estiver dividido, substitua o caminho de `--input` pelo arquivo `NOME_DO_BACKUP.tar.gz.enc.part0001`.

O modo `database` valida o hash, descriptografa o pacote, extrai o dump e executa `pg_restore` no banco definido pelo Compose do projeto informado em `--project-dir`. A aplicação é parada durante a restauração e iniciada novamente ao final.

Para restaurar uma única tabela do schema `public`, pode-se acrescentar `--table NOME_DA_TABELA`. Sem essa opção, o dump inteiro é restaurado.

### 8.4. Restaurar o projeto completo

> **Atenção:** use uma pasta de destino nova e vazia. Não use a pasta atual do projeto em produção. A restauração completa também executa comandos Docker Compose no diretório de destino.

Crie um destino vazio:

```bash
mkdir -p ~/restauracao-completa
```

Execute:

```bash
cd /home/ubuntu/Trabalho-Web-III

./scripts/restore.sh \
  --input ~/backup-restore/NOME_DO_BACKUP.tar.gz.enc \
  --sha256 HASH_SHA256_COMPLETO \
  --mode full \
  --target ~/restauracao-completa
```

Se estiver dividido, informe a primeira parte `.part0001`.

O modo `full`:

1. Reúne as partes, se necessário, e valida o SHA-256.
2. Descriptografa e verifica a autenticação AES-GCM.
3. Extrai os arquivos do projeto no destino vazio.
4. Restaura o dump PostgreSQL usando o Docker Compose desse destino.
5. Executa `docker compose up -d --build` no destino.

Depois, revise o arquivo `.env`, os serviços, as portas, o domínio, o proxy e os certificados antes de direcionar tráfego para a instalação restaurada. A restauração dos arquivos do projeto não recria automaticamente configurações externas da VPS.

### 8.5. Recuperação após perda total da VPS

Em um servidor novo:

1. Instale Ubuntu, Docker Engine e o plugin Docker Compose.
2. Crie um usuário com permissão para executar Docker.
3. Clone o repositório e entre na pasta do projeto.
4. Instale o ambiente `.venv-backup` conforme a seção 5.
5. Baixe o backup do Telegram e todas as partes para `~/backup-restore`.
6. Disponibilize a senha do backup conforme a seção 8.2.
7. Execute a restauração completa em um diretório vazio conforme a seção 8.4.
8. Revise as configurações externas, firewall, domínio, Caddy e certificados antes de publicar o serviço.

A senha de descriptografia e o arquivo do backup são indispensáveis. O arquivo de configuração do bot pode ser recriado depois para reativar os próximos backups.

## 9. Verificações e solução de problemas

| Sintoma | Verificação |
|---|---|
| `Backup virtual environment not found` | Recrie `.venv-backup` e instale `scripts/requirements-backup.txt`. |
| `Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID` | Verifique as variáveis no arquivo `/etc/trabalho-web-iii-backup.env` e suas permissões. |
| `Configure BACKUP_PASSPHRASE` | Configure uma senha com pelo menos 16 caracteres. |
| Erro de acesso ao Docker | Confirme que o usuário do serviço pertence ao grupo `docker` e que o daemon está ativo. |
| PostgreSQL não aceita conexões | Confira `docker compose ps` e os logs do serviço `db`. |
| SHA-256 não corresponde | Baixe novamente o arquivo e todas as partes; confirme o hash copiado da legenda. |
| Partes ausentes ou numeração inválida | Coloque todas as partes na mesma pasta e mantenha os nomes originais. |
| Senha incorreta ou autenticação GCM falhou | Confirme a senha e se o arquivo não foi alterado. |

Comandos úteis:

```bash
docker compose ps
docker compose logs --tail=100 db
sudo systemctl status trabalho-web-iii-backup.timer
sudo journalctl -u trabalho-web-iii-backup.service -n 100 --no-pager
```

## 10. Boas práticas

- Mantenha a senha de descriptografia em um gerenciador de senhas separado do Telegram.
- Restrinja as permissões do arquivo `/etc/trabalho-web-iii-backup.env`.
- Não envie arquivos `.env`, tokens, senhas ou backups descriptografados ao Git.
- Mantenha cópias independentes dos backups importantes; uma única conta Telegram não deve ser a única estratégia de retenção.
- Monitore periodicamente o timer e os logs do serviço.
- Faça testes periódicos de restauração em ambiente isolado. A confirmação de upload não comprova, sozinha, que a recuperação funcionará.
- Planeje atualizar o Python do servidor para uma versão atualmente suportada pelo projeto `cryptography`.

