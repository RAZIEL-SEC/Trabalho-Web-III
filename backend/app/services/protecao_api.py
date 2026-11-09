import hashlib

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
        window_start = EXCLUDED.window_start
    RETURNING request_count
""")


def _chave_ip(ip: str) -> str:
    # Não persiste o endereço IP em texto puro na tabela de limitação.
    digest = hashlib.sha256(ip.encode("utf-8")).hexdigest()
    return f"ip:{digest}"


def limitar_api(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
) -> None:
    """Limite compartilhado entre workers/processos, persistido no PostgreSQL."""
    ip = request.client.host if request.client else "desconhecido"
    limites = (
        (f"user:{usuario.id}", settings.api_rate_limit_user_per_minute),
        (_chave_ip(ip), settings.api_rate_limit_ip_per_minute),
    )

    for chave, limite in limites:
        quantidade = db.execute(
            _UPSERT_CONTADOR, {"bucket_key": chave}
        ).scalar_one()
        if quantidade > limite:
            # Persiste o contador mesmo quando a requisição é rejeitada.
            db.commit()
            raise HTTPException(
                status_code=429,
                detail="Limite de requisições excedido. Aguarde um minuto.",
                headers={"Retry-After": "60"},
            )

    # Mantém o contador consistente entre processos. O endpoint inicia uma
    # nova transação na mesma Session depois desta confirmação.
    db.commit()
