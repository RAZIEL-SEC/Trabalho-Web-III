# Trabalho-Web-III

Projeto desenvolvido na disciplina de Web 3: uma aplicação web para uma ONG sem fins lucrativos, com site institucional, painel administrativo e gerenciamento de estoque integrado a PostgreSQL.

## Ambientes publicados

- **Site institucional:** https://trabalho-web-iii.razielsec01.workers.dev
- **Painel:** https://amigosdozealguem.duckdns.org/estoque/login.html

## Execução do projeto

```bash
git clone https://github.com/RAZIEL-SEC/Trabalho-Web-III.git
cd Trabalho-Web-III

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt

# Linux
cp .env.example backend/.env

docker compose up -d
cd backend
uvicorn app.main:app --reload
```

## Segurança e operação

A aplicação utiliza proteção CSRF, controle de sessão, limitação de requisições, auditoria e migrações SQL idempotentes. Em produção, a API deve ficar atrás do proxy reverso, com cabeçalhos encaminhados confiáveis e configuração segura de cookies.

Consulte [docs/operacao.md](docs/operacao.md) para orientações operacionais e [docs/contrato-api.md](docs/contrato-api.md) para o contrato da API.

## Backup e recuperação

O projeto possui backup automatizado do código e do PostgreSQL, com criptografia **AES-256-GCM**, derivação de chave **Argon2id**, verificação **SHA-256** e envio ao Telegram. O agendamento diário é realizado por um timer do systemd.

A rotina foi ativada na VPS e um backup real foi enviado ao Telegram. A restauração também foi validada em um PostgreSQL isolado: o dump foi recuperado e as seis tabelas do banco foram listadas com sucesso. O ambiente temporário de teste foi removido após a validação.

A documentação com instalação, configuração, execução manual, agendamento, restauração completa e recuperação do banco está em **[docs/backup.md](docs/backup.md)**.

## Documentação adicional

- [Operação e implantação](docs/operacao.md)
- [Contrato da API](docs/contrato-api.md)
- [Testes](docs/testes.md)
- [Backup e recuperação](docs/backup.md)
