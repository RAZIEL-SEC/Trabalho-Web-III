from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.routers import auth, itens, movimentacoes, usuarios

app = FastAPI(title="Estoque - Amigos do Zé Alguém")
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(itens.router)
app.include_router(movimentacoes.router)


@app.get("/saude")
def saude(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


# telas do sistema, servidas na mesma origem da API (o cookie de sessão depende disso)
PASTA_ESTOQUE = Path(__file__).resolve().parents[2] / "estoque"
app.mount("/estoque", StaticFiles(directory=PASTA_ESTOQUE, html=True), name="estoque")
