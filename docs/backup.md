# Backup e recuperação do Trabalho-Web-III

Este documento descreve a rotina de backup da VPS, o envio ao Telegram e os procedimentos de recuperação.

## Estado atual

- Backup manual executado com sucesso e recebido pelo Telegram.
- Timer diário do systemd habilitado e ativo na VPS.
- Restauração real do dump PostgreSQL executada com sucesso em um container isolado.
- As seis tabelas esperadas foram recuperadas: `auditoria`, `idempotency_keys`, `itens`, `movimentacoes`, `rate_limit_counters` e `usuarios`.
- Container, volume, rede e arquivos usados no teste foram removidos após a validação.

A restauração foi testada em ambiente isolado; isso não significa que uma recuperação completa de uma VPS nova tenha sido executada. O procedimento de recuperação completa está implementado e documentado abaixo.

## Escopo do backup

O backup reúne:

- Arquivos do projeto, incluindo arquivos `.env` presentes dentro da pasta do repositório.
- Dump PostgreSQL do banco `estoque`, gerado em formato customizado por `pg_dump -Fc`.
- Manifesto com formato, versão, data e conteúdo do pacote.

São excluídos, entre outros, `.git`, ambientes virtuais, caches, `node_modules`, `.wrangler`, diretórios locais de backup, links simbólicos e arquivos `.pyc`, `.enc` e `.dump`.

Configurações externas à pasta do projeto **não** são incluídas: Caddy, certificados TLS, firewall, DNS, regras de rede e configurações do sistema operacional precisam ser recuperados separadamente.

## Criptografia e integridade

- **AES-256-GCM:** criptografa e autentica o conteúdo.
- **Argon2id:** deriva a chave a partir de `BACKUP_PASSPHRASE`, com salt aleatório por arquivo.
- **SHA-256:** identifica o arquivo criptografado; o hash é enviado na legenda do Telegram e é obrigatório para restaurar.
- **Divisão de arquivos:** backups acima de 40 MiB são enviados em partes numeradas. Todas as partes devem ser baixadas para a mesma pasta.

A senha não é armazenada no backup nem enviada ao Telegram. Guarde-a em um gerenciador de senhas e em local separado da VPS. Se ela for perdida, o conteúdo não poderá ser recuperado.

## Requisitos

A instalação atual considera:

- Ubuntu e Docker Engine com o plugin Docker Compose.
- Usuário `ubuntu` com acesso ao Docker (grupo `docker`).
- Projeto em `/home/ubuntu/Trabalho-Web-III`.
- Python e as dependências listadas em `scripts/requirements-backup.txt`.
- Acesso HTTPS de saída a `api.telegram.org`.
- Bot do Telegram e chat privado configurados.

Recomenda-se Python 3.10 ou superior. O ambiente atualmente instalado na VPS usa Python 3.8.10; ele executou o backup e a restauração de teste, mas a biblioteca `cryptography` emitiu um aviso de descontinuação para essa versão.

## 1. Configurar o Telegram e as credenciais

Crie um bot com o [@BotFather](https://t.me/BotFather), inicie uma conversa privada com ele e obtenha o token e o `chat_id`.

Na VPS, crie o arquivo de configuração fora do repositório:

```bash
sudo install -m 600 /dev/null /etc/trabalho-web-iii-backup.env
sudo chown root:ubuntu /etc/trabalho-web-iii-backup.env
sudo chmod 640 /etc/trabalho-web-iii-backup.env
sudoedit /etc/trabalho-web-iii-backup.env
```

Conteúdo:

```dotenv
TELEGRAM_BOT_TOKEN=TOKEN_DO_BOT
TELEGRAM_CHAT_ID=ID_DO_CHAT_PRIVADO
BACKUP_PASSPHRASE=SENHA_FORTE_E_EXCLUSIVA
```

A senha deve ter pelo menos 16 caracteres. Para gerar uma senha aleatória:

```bash
openssl rand -hex 32
```

Guarde a senha fora da VPS. Nunca versione esse arquivo, compartilhe o token ou coloque credenciais em logs.

## 2. Instalar as dependências

Na VPS:

```bash
cd /home/ubuntu/Trabalho-Web-III

sudo apt update
sudo apt install -y python3-venv

python3 -m venv .venv-backup
.venv-backup/bin/python -m pip install --upgrade pip
.venv-backup/bin/python -m pip install -r scripts/requirements-backup.txt

chmod 750 scripts/backup.sh scripts/restore.sh
```

O ambiente `.venv-backup` é separado do ambiente da aplicação e não deve ser commitado.

## 3. Executar backup manual

Com os serviços Docker Compose em execução e o arquivo de credenciais configurado:

```bash
cd /home/ubuntu/Trabalho-Web-III
./scripts/backup.sh
```

O script carrega `/etc/trabalho-web-iii-backup.env`, exporta o banco, empacota os arquivos, criptografa o arquivo e envia o resultado ao Telegram. A execução só é considerada concluída quando o Telegram confirma o recebimento.

## 4. Agendamento diário com systemd

As unidades ficam em `deploy/`:

- `trabalho-web-iii-backup.service`: executa o backup como usuário `ubuntu`.
- `trabalho-web-iii-backup.timer`: agenda a execução diária.

Instalação:

```bash
cd /home/ubuntu/Trabalho-Web-III

sudo install -m 644 deploy/trabalho-web-iii-backup.service /etc/systemd/system/
sudo install -m 644 deploy/trabalho-web-iii-backup.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now trabalho-web-iii-backup.timer
```

O timer está configurado para **03:15 no fuso horário da VPS**, com atraso aleatório de até cinco minutos e recuperação de execuções perdidas (`Persistent=true`). Na VPS atual, configurada em UTC, isso corresponde a aproximadamente **00:15 no horário de Brasília**, mais o atraso aleatório.

Verificar o próximo disparo e o estado:

```bash
timedatectl
systemctl list-timers --all | grep trabalho-web-iii-backup
sudo systemctl status trabalho-web-iii-backup.timer
```

Consultar logs e executar manualmente pelo systemd:

```bash
sudo journalctl -u trabalho-web-iii-backup.service -n 100 --no-pager
sudo systemctl start trabalho-web-iii-backup.service
```

Desativar o agendamento:

```bash
sudo systemctl disable --now trabalho-web-iii-backup.timer
```

O serviço é do tipo `oneshot`; por isso, aparecer como `inactive (dead)` depois de uma execução bem-sucedida é normal. O timer, por outro lado, deve permanecer `active (waiting)`.

## 5. Preparar a restauração

Baixe do Telegram o arquivo criptografado e, quando houver divisão, **todas** as partes. Coloque-as na mesma pasta e mantenha os nomes originais.

```bash
mkdir -p ~/backup-restore
chmod 700 ~/backup-restore
```

O arquivo único termina em `.tar.gz.enc`. Para arquivos divididos, informe ao restaurador a primeira parte, terminada em `.part0001`; ele reúne as partes em ordem e valida o SHA-256 do arquivo completo.

A restauração solicita a senha de forma interativa. Também é possível disponibilizá-la temporariamente no ambiente sem incluí-la no comando:

```bash
read -rsp "Senha do backup: " BACKUP_PASSPHRASE
echo
export BACKUP_PASSPHRASE
```

Depois da operação:

```bash
unset BACKUP_PASSPHRASE
```

O script `restore.sh` não carrega automaticamente o arquivo de ambiente do backup; use a solicitação interativa ou exporte `BACKUP_PASSPHRASE` como acima.

## 6. Restaurar somente o banco de dados

> **Atenção:** esse modo sobrescreve objetos e dados do banco indicado. Faça um backup do estado atual e confira cuidadosamente o diretório do projeto antes de confirmar.

```bash
cd /home/ubuntu/Trabalho-Web-III

./scripts/restore.sh \
  --input ~/backup-restore/NOME_DO_BACKUP.tar.gz.enc \
  --sha256 HASH_SHA256_COMPLETO \
  --mode database \
  --project-dir /home/ubuntu/Trabalho-Web-III \
  --confirm-overwrite
```

Se o backup estiver dividido, use o caminho da primeira parte `.part0001`.

O restaurador valida o SHA-256, autentica e descriptografa o arquivo, extrai o dump e executa `pg_restore` no banco do Compose indicado por `--project-dir`. A aplicação é parada durante a operação e iniciada novamente ao final.

Para restaurar apenas uma tabela do schema `public`, acrescente, por exemplo, `--table usuarios`. A restauração parcial pode depender de outras tabelas, constraints e chaves estrangeiras; avalie essas dependências antes de usá-la.

## 7. Restaurar o projeto completo

> **Atenção:** use um diretório novo e vazio. Não execute esse modo apontando para a pasta do projeto em produção. O procedimento inicia containers Docker Compose no diretório de destino.

```bash
mkdir -p ~/restauracao-completa

cd /home/ubuntu/Trabalho-Web-III
./scripts/restore.sh \
  --input ~/backup-restore/NOME_DO_BACKUP.tar.gz.enc \
  --sha256 HASH_SHA256_COMPLETO \
  --mode full \
  --target ~/restauracao-completa
```

O modo completo:

1. Reúne as partes, se necessário, e valida o SHA-256.
2. Descriptografa e verifica a autenticação AES-GCM.
3. Extrai os arquivos do projeto no destino vazio.
4. Inicia o serviço PostgreSQL do Compose extraído e restaura o dump.
5. Executa `docker compose up -d --build` no diretório de destino.

Após a restauração, revise variáveis de ambiente, portas, domínio, proxy, certificados e firewall antes de direcionar tráfego para a instalação recuperada.

## 8. Recuperação após perda total da VPS

1. Prepare uma VPS nova com Ubuntu, Docker Engine e Docker Compose.
2. Clone o repositório em um diretório de trabalho e instale as dependências do backup conforme a seção 2.
3. Baixe o backup do Telegram e todas as partes para `~/backup-restore`.
4. Disponibilize a senha conforme a seção 5.
5. Execute a restauração completa em um diretório vazio conforme a seção 7.
6. Revise e recrie as configurações externas que não fazem parte do backup: proxy reverso, DNS, TLS, firewall e regras de rede.
7. Valide os containers, logs e o endpoint de saúde antes de liberar o serviço.

## 9. Diagnóstico

| Sintoma | Verificação |
|---|---|
| Ambiente virtual não encontrado | Recrie `.venv-backup` e instale `scripts/requirements-backup.txt`. |
| Token ou chat ID ausente | Confira `/etc/trabalho-web-iii-backup.env` e as permissões. |
| Senha ausente ou curta | Configure `BACKUP_PASSPHRASE` com pelo menos 16 caracteres. |
| Erro de acesso ao Docker | Confira o grupo `docker` e o estado do daemon. |
| PostgreSQL indisponível | Verifique `docker compose ps` e os logs do serviço `db`. |
| SHA-256 divergente | Baixe novamente o arquivo e todas as partes; confira o hash da legenda. |
| Autenticação GCM falhou | Confirme a senha e a integridade do arquivo. |

Comandos úteis:

```bash
docker compose ps
docker compose logs --tail=100 db
sudo systemctl status trabalho-web-iii-backup.timer
sudo journalctl -u trabalho-web-iii-backup.service -n 100 --no-pager
```

## Boas práticas

- Mantenha a senha separada do Telegram e da VPS.
- Restrinja as permissões de `/etc/trabalho-web-iii-backup.env`.
- Mantenha cópias independentes dos backups importantes.
- Monitore o timer e os logs do serviço.
- Faça testes de restauração isolados após alterações relevantes no banco ou no formato do backup.
- Não confunda confirmação de upload com validação de recuperação: a restauração isolada deve ser verificada periodicamente.
