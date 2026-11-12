# Backup e recuperação do Trabalho-Web-III

O backup roda fora do FastAPI. Ele exporta o PostgreSQL 16, inclui os arquivos do projeto (inclusive .env, se existir), compacta, criptografa com AES-256-GCM e chave derivada por Argon2id, e envia ao Telegram.

> Escopo: projeto e banco estoque. Configurações externas da VPS (Caddy, firewall, DNS, certificados e outros serviços fora do repositório) não são capturadas automaticamente e precisam de documentação/cópia separada.

## Proteção e conteúdo

- Dump PostgreSQL em formato custom, restaurável por pg_restore.
- Código, migrations, Docker Compose, Dockerfile, scripts, frontend e documentação.
- Arquivos .env incluídos dentro do arquivo cifrado.
- AES-256-GCM fornece confidencialidade e autenticação; Argon2id deriva a chave.
- SHA-256 do arquivo cifrado aparece na legenda do Telegram.
- Arquivos maiores que 40 MiB são enviados em partes numeradas. Baixe todas e concatene em ordem antes da restauração.
- .git, .venv, caches, node_modules e backups locais são excluídos.

A senha BACKUP_PASSPHRASE nunca é enviada ao Telegram. Se for perdida, o backup não poderá ser aberto. Guarde-a em gerenciador de senhas e em local separado da VPS.

## 1. Bot Telegram

Crie um bot pelo @BotFather, inicie conversa com ele (ou adicione-o ao grupo/canal), obtenha o chat_id e permita que ele envie documentos.

Crie o arquivo privado na VPS:

~~~bash
sudo install -m 600 -o ubuntu -g ubuntu /dev/null /etc/trabalho-web-iii-backup.env
sudo nano /etc/trabalho-web-iii-backup.env
~~~

Conteúdo com valores reais:

~~~bash
TELEGRAM_BOT_TOKEN=TOKEN_DO_BOT
TELEGRAM_CHAT_ID=ID_DO_CHAT
BACKUP_PASSPHRASE=SENHA_LONGA_E_ALEATORIA
~~~

Gere a senha com openssl rand -base64 48 e guarde-a fora do servidor. Não coloque token nem senha no Git.

## 2. Dependências e primeiro teste

Na VPS, dentro do projeto:

~~~bash
sudo apt-get update
sudo apt-get install -y python3-pip
python3 -m pip install --user -r backend/requirements.txt
docker compose ps
docker compose exec -T db pg_isready -U estoque -d estoque
bash scripts/backup.sh
~~~

Se o sistema bloquear instalação pelo PEP 668, crie um venv dedicado e ajuste o Python chamado em scripts/backup.sh e no serviço systemd. O envio só é considerado concluído quando o Telegram confirmar todos os documentos.

## 3. Agendamento diário

O timer está configurado para 03:15 no horário local da VPS, com atraso aleatório de até cinco minutos.

~~~bash
sudo cp deploy/trabalho-web-iii-backup.service /etc/systemd/system/
sudo cp deploy/trabalho-web-iii-backup.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now trabalho-web-iii-backup.timer
systemctl list-timers trabalho-web-iii-backup.timer
~~~

O usuário ubuntu precisa ter acesso de leitura ao projeto e ao socket Docker (grupo docker).

Executar/diagnosticar:

~~~bash
sudo systemctl start trabalho-web-iii-backup.service
sudo systemctl status trabalho-web-iii-backup.service
sudo journalctl -u trabalho-web-iii-backup.service -n 100 --no-pager
~~~

## 4. Recuperação completa em uma VPS nova

1. Instale Docker Engine e Docker Compose.
2. Obtenha uma cópia confiável do repositório em um diretório separado (por exemplo, /opt/backup-bootstrap), contendo scripts/backup_manager.py. Instale argon2-cffi e cryptography no Python que executará o restaurador.
3. Baixe o arquivo .enc do Telegram. Se ele tiver partes, concatene-as em ordem:

~~~bash
cat trabalho-web-iii_*.enc.part* > trabalho-web-iii.enc
~~~

4. Disponibilize BACKUP_PASSPHRASE no ambiente sem colocá-la no histórico do terminal.
5. Execute com destino vazio:

~~~bash
python3 scripts/backup_manager.py restore --input /caminho/trabalho-web-iii.enc --mode full --target /opt/Trabalho-Web-III
~~~

O script autentica e descriptografa o arquivo, extrai o projeto, inicia PostgreSQL, restaura o dump e reconstrói os serviços. Depois confira docker compose ps, logs, endpoint /saude, proxy, DNS, certificados e firewall.

## 5. Recuperação do banco ou de uma tabela

No projeto atual, baixar e descriptografar o backup e executar:

Banco inteiro (sobrescreve objetos existentes):

~~~bash
python3 scripts/backup_manager.py restore --input /caminho/trabalho-web-iii.enc --mode database --project-dir /home/ubuntu/Trabalho-Web-III --confirm-overwrite
~~~

Uma tabela (substitui a tabela de destino):

~~~bash
python3 scripts/backup_manager.py restore --input /caminho/trabalho-web-iii.enc --mode database --project-dir /home/ubuntu/Trabalho-Web-III --table usuarios --confirm-overwrite
~~~

O modo parcial usa pg_restore --table e pode depender de outras tabelas/foreign keys. Teste em ambiente isolado antes de usar em produção.

## 6. Testes antes de confiar no backup

- Fazer backup manual e confirmar recebimento no Telegram.
- Baixar o arquivo/partes, conferir SHA-256 e testar a descriptografia.
- Restaurar em VPS/ambiente isolado, nunca diretamente sobre produção.
- Conferir docker compose ps, logs e /saude.
- Repetir após alterações relevantes no schema.

Não considere a rotina pronta para produção antes de concluir uma restauração real. Mantenha também uma cópia independente do Telegram quando possível.
