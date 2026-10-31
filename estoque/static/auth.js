// Incluído em todas as telas internas (menos o login).
// Sem sessão válida, volta para o login. `sessao` resolve com {id, nome, email, perfil}.
const sessao = fetch("/auth/eu").then((r) => {
  if (r.status === 401) {
    window.location.href = "login.html?expirou=1";
    return null;
  }
  return r.json();
});

// Itens marcados com data-so-admin só aparecem para administradores.
// (A API também recusa: isto é só para não mostrar o que a pessoa não pode usar.)
sessao.then((u) => {
  if (u && u.perfil === "admin") {
    document.querySelectorAll("[data-so-admin]").forEach((el) => (el.hidden = false));
  }
});

function encerrar(url) {
  fetch(url, { method: "POST" }).then(() => {
    window.location.href = "login.html";
  });
}

document.addEventListener("click", (e) => {
  // data-sair: encerra só esta sessão
  if (e.target.closest("[data-sair]")) encerrar("/auth/logout");
  // data-sair-todos: encerra a sessão em todos os dispositivos
  if (e.target.closest("[data-sair-todos]")) encerrar("/auth/sair-de-todos");
});
