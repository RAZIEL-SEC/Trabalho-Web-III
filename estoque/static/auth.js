const sessao = fetch("/auth/eu").then((r) => {
  if (r.status === 401) {
    window.location.href = "login.html?expirou=1";
    return null;
  }
  return r.json();
});

let tokenCsrfPromise;
async function obterTokenCsrf() {
  if (!tokenCsrfPromise) {
    tokenCsrfPromise = fetch("/auth/csrf").then(async (r) => {
      if (r.status === 401) {
        window.location.href = "login.html?expirou=1";
        throw new Error("Sessão expirada.");
      }
      if (!r.ok) throw new Error("Não foi possível validar a sessão.");
      return (await r.json()).csrf_token;
    }).catch((erro) => {
      tokenCsrfPromise = null;
      throw erro;
    });
  }
  return tokenCsrfPromise;
}

async function apiFetch(url, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = new Headers(options.headers || {});
  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    headers.set("X-CSRF-Token", await obterTokenCsrf());
  }
  return fetch(url, { ...options, headers });
}

sessao.then((u) => {
  if (u && u.perfil === "admin") {
    document.querySelectorAll("[data-so-admin]").forEach((el) => (el.hidden = false));
  }
});

function encerrar(url) {
  apiFetch(url, { method: "POST" }).then(() => {
    window.location.href = "login.html";
  }).catch(() => {
    window.location.href = "login.html";
  });
}

document.addEventListener("click", (e) => {
  if (e.target.closest("[data-sair]")) encerrar("/auth/logout");
  if (e.target.closest("[data-sair-todos]")) encerrar("/auth/sair-de-todos");
});
