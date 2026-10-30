# Trabalho-Web-III
Projeto desenvolvido na disciplina de Web 3, com o objetivo de criar um sistema web completo para uma ONG sem fins lucrativos. A aplicação conta com um site integrado a um banco de dados, permitindo o gerenciamento e a organização das informações da instituição de forma simples, segura e eficiente.

git clone https://github.com/RAZIEL-SEC/Trabalho-Web-III.git
cd Trabalho-Web-III

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r backend/requirements.txt

// Linux: cp .env.example backend/.env       

// Windows: copy .env.example backend\.env

docker compose up -d
cd backend
uvicorn app.main:app --reload

https://trabalho-web-iii.razielsec01.workers.dev/templates/cadastro
