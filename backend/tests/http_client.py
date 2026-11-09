from uuid import uuid4

from fastapi.testclient import TestClient


class IdempotentTestClient(TestClient):
    """Fornece uma chave nova por chamada legada dos testes.

    Testes específicos de idempotência passam a chave explicitamente para
    repetir a mesma operação ou validar conflito de payload.
    """

    def post(self, url, *args, **kwargs):
        if url == "/movimentacoes":
            headers = dict(kwargs.get("headers") or {})
            headers.setdefault("Idempotency-Key", str(uuid4()))
            kwargs["headers"] = headers
        return super().post(url, *args, **kwargs)
