import hashlib
import ipaddress

from fastapi import Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, get_usuario_atual
from app.models.usuario import Usuario


_UPSERT_CONTADOR = text("""
    INSERT INTO rate_limit_counters (bucket_key, window_start, request_count)
    VALUES (:bucket_key, date_trunc('minute', clock_timestamp()), 1)
    ON CONFLICT (bucket_key) DO UPDATE
    SET
        request_count = CASE
            WHEN rate_limit_counters.window_start
                 < EXCLUDED.window_start THEN 1
            ELSE rate_limit_counters.request_count + 1
        END,
        window_start = CASE
            WHEN rate_limit_counters.window_start
                 < EXCLUDED.window_start THEN EXCLUDED.window_start
            ELSE rate_limit_counters.window_start
        END
    RETURNING request_count
""")


def _ip_do_cliente(request: Request) -> str:
    """Obtém o IP enviado pelo proxy reverso confiável ou o peer direto.

    O backend só deve ser publicado atrás do proxy configurado, que precisa
    sobrescrever X-Forwarded-For. O serviço não deve ficar exposto diretamente.
    """
    encaminhado = request.headers.get("x-forwarded-for")
    candidato = encaminhado.split(",", 1)[0].strip() if encaminhado else ""
    if candidato:
        try:
            return str(ipaddress.ip_address(candidato))
        except ValueError:
            pass

    peer = request.client.host if request.client else "desconhecido"
    try:
        return str(ipaddress.ip_address(peer))
    except ValueError:
        return "desconhecido"


def _chave_ip(ip: str) -> str:
    digest = hashlib.sha256(ip.encode("utf-8")).hexdigest()
    return f"ip:{digest}"


def _incrementar(db: Session, chave: str, limite: int) -> None:
    quantidade = db.execute(
        _UPSERT_CONTADOR, {"bucket_key": chave}
    ).scalar_one()
    if quantidade > limite:
        db.commit()
        raise HTTPException(
            status_code=429,
            detail="Limite de requisições excedido. Aguarde um minuto.",
            headers={"Retry-After": "60"},
        )


def limitar_por_ip(
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    """Limite compartilhado por IP para endpoints públicos, como o login."""
    _incrementar(
        db,
        _chave_ip(_ip_do_cliente(request)),
        settings.api_rate_limit_ip_per_minute,
    )
    db.commit()


def limitar_api(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
) -> None:
    """Limites compartilhados por usuário e IP, persistidos no PostgreSQL."""
    ip = _ip_do_cliente(request)
    _incrementar(db, f"user:{usuario.id}", settings.api_rate_limit_user_per_minute)
    _incrementar(db, _chave_ip(ip), settings.api_rate_limit_ip_per_minute)
    # O contador é confirmado antes da operação de negócio, para não ser
    # revertido junto com um eventual rollback do endpoint.
    db.commit()
