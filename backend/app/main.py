from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.deps import get_db

app = FastAPI(title="Estoque - Amigos do Zé Alguém")

@app.get("/saude")
def saude(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}