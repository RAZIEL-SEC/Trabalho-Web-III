from uuid import uuid4

from fastapi.testclient import TestClient


class IdempotentTestClient(TestClient):
    """Simula navegador same-origin e mantém o token CSRF da sessão."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._csrf_token = None

    def request(self, method, url, *args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        metodo = method.upper()
        if metodo not in {"GET", "HEAD", "OPTIONS"}:
            headers.setdefault("Origin", "https://testserver")

        if metodo == "POST" and url == "/auth/login":
            kwargs["headers"] = headers
            response = super().request(method, url, *args, **kwargs)
            if response.status_code == 200:
                token_response = super().get("/auth/csrf")
                if token_response.status_code == 200:
                    self._csrf_token = token_response.json()["csrf_token"]
            return response

        if (
            metodo not in {"GET", "HEAD", "OPTIONS"}
            and url != "/auth/login"
            and self.cookies.get("access_token")
            and "X-CSRF-Token" not in headers
        ):
            if self._csrf_token is None:
                token_response = super().get("/auth/csrf")
                if token_response.status_code == 200:
                    self._csrf_token = token_response.json()["csrf_token"]
            if self._csrf_token is not None:
                headers["X-CSRF-Token"] = self._csrf_token

        kwargs["headers"] = headers
        return super().request(method, url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        if url == "/movimentacoes":
            headers = dict(kwargs.get("headers") or {})
            headers.setdefault("Idempotency-Key", str(uuid4()))
            kwargs["headers"] = headers
        return super().post(url, *args, **kwargs)
