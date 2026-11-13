from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.csrf import validar_requisicao_csrf
from app.core.deps import get_db
from app.routers import auth, classificacoes, itens, movimentacoes, usuarios

app = FastAPI(title="Estoque - Amigos do Zé Alguém")
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(itens.router)
app.include_router(classificacoes.router)
app.include_router(movimentacoes.router)


@app.middleware("http")
async def protecao_csrf(request: Request, call_next):
    if not validar_requisicao_csrf(request):
        return JSONResponse(
            status_code=403,
            content={"detail": "Requisição bloqueada pela proteção CSRF."},
        )
    return await call_next(request)


@app.get("/saude")
def saude(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def inicio():
    return RedirectResponse("/estoque/", status_code=307)


@app.get("/login", include_in_schema=False)
def tela_login():
    return RedirectResponse("/estoque/login", status_code=307)


@app.get("/usuario", include_in_schema=False)
def tela_usuarios():
    return RedirectResponse("/estoque/usuarios", status_code=307)


# API e painel são servidos na mesma origem.
PASTA_ESTOQUE = Path(__file__).resolve().parents[2] / "estoque"
class PainelStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        if path.endswith(".html"):
            destino = "/estoque/" if path == "index.html" else f"/estoque/{path[:-5]}"
            query = scope.get("query_string", b"").decode("latin-1")
            if query:
                destino = f"{destino}?{query}"
            return RedirectResponse(destino, status_code=308)

        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as erro:
            if erro.status_code != 404:
                raise
            return await super().get_response(f"{path}.html", scope)


app.mount("/estoque", PainelStaticFiles(directory=PASTA_ESTOQUE, html=True), name="estoque")
