from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.routers import auth, itens

app = FastAPI(title="Estoque - Amigos do Zé Alguém")
app.include_router(auth.router)
app.include_router(itens.router)


@app.get("/saude")
def saude(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
