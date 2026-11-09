# Trabalho-Web-III
Projeto desenvolvido na disciplina de Web 3, com o objetivo de criar um sistema web completo para uma ONG sem fins lucrativos. A aplicação conta com um site integrado a um banco de dados, permitindo o gerenciamento e a organização das informações da instituição de forma simples, segura e eficiente.

git clone https://github.com/RAZIEL-SEC/Trabalho-Web-III.git
cd Trabalho-Web-III

python3 -m venv .venv
source .venv/bin/activate          // Windows: .venv\Scripts\activate
python -m pip install -r backend/requirements.txt

// Linux: cp .env.example backend/.env       

// Windows: copy .env.example backend\.env

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
