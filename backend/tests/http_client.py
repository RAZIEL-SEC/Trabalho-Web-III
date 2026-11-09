from uuid import uuid4

from fastapi.testclient import TestClient


class IdempotentTestClient(TestClient):
    """Simula chamadas same-origin e envia o token CSRF nas mutações autenticadas."""

    def request(self, method, url, *args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        if method.upper() not in {"GET", "HEAD", "OPTIONS"}:
            headers.setdefault("Origin", "https://testserver")
            if url != "/auth/login" and self.cookies.get("access_token"):
                token_response = super().get("/auth/csrf")
                if token_response.status_code == 200:
                    headers.setdefault(
                        "X-CSRF-Token", token_response.json()["csrf_token"]
                    )
        kwargs["headers"] = headers
        return super().request(method, url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        if url == "/movimentacoes":
            headers = dict(kwargs.get("headers") or {})
            headers.setdefault("Idempotency-Key", str(uuid4()))
            kwargs["headers"] = headers
        return super().post(url, *args, **kwargs)
