const corpo = document.getElementById("tabela");
const msg = document.getElementById("msg");
const form = document.getElementById("form-usuario");

function mostrar(texto, ok) {
  msg.textContent = texto;
  msg.dataset.estado = ok ? "ok" : "erro";
}

function erroDaApi(dados) {
  if (typeof dados.detail === "string") return dados.detail;
  if (Array.isArray(dados.detail)) return "Confira os campos: nome, e-mail válido e senha com 10+ caracteres.";
  return "Não foi possível concluir.";
}

function celula(texto) {
  const td = document.createElement("td");
  td.textContent = texto; // textContent: nada que venha do banco vira HTML
  return td;
}

async function alterar(id, mudanca) {
  const r = await fetch(`/usuarios/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(mudanca),
  });
  if (!r.ok) {
    mostrar(erroDaApi(await r.json().catch(() => ({}))), false);
    return;
  }
  mostrar("Usuário atualizado.", true);
  carregar();
}

async function carregar() {
  const r = await fetch("/usuarios");
  if (r.status === 401) return (window.location.href = "login.html");
  if (r.status === 403) return (window.location.href = "itens.html");
  const usuarios = await r.json();

  corpo.replaceChildren();
  for (const u of usuarios) {
    const tr = document.createElement("tr");
    tr.append(
      celula(u.nome),
      celula(u.email),
      celula(u.perfil === "admin" ? "Administrador" : "Operador"),
      celula(u.ativo ? "Ativo" : "Desativado"),
    );
    const acoes = document.createElement("td");
    const botao = document.createElement("button");
    botao.type = "button";
    botao.textContent = u.ativo ? "Desativar" : "Reativar";
    botao.addEventListener("click", () => alterar(u.id, { ativo: !u.ativo }));
    acoes.append(botao);
    tr.append(acoes);
    corpo.append(tr);
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const botao = form.querySelector("button[type=submit]");
  botao.disabled = true;
  const dados = Object.fromEntries(new FormData(form));
  try {
    const r = await fetch("/usuarios", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });
    if (r.ok) {
      form.reset();
      mostrar("Usuário cadastrado.", true);
      carregar();
    } else {
      mostrar(erroDaApi(await r.json().catch(() => ({}))), false);
    }
  } catch {
    mostrar("Sem conexão com o servidor.", false);
  }
  botao.disabled = false;
});

// só administradores ficam nesta tela
sessao.then((u) => {
  if (!u) return;
  if (u.perfil !== "admin") {
    window.location.href = "itens.html";
    return;
  }
  carregar();
});
