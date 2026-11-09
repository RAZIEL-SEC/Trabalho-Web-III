const corpo = document.getElementById("tabela");
const msg = document.getElementById("msg");
const form = document.getElementById("form-usuario");
let usuarioAtual = null;

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
  const r = await apiFetch(`/usuarios/${id}`, {
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

async function excluir(id, nome, botao) {
  if (!confirm(`Tem certeza que deseja excluir permanentemente o usuário "${nome}"? Esta ação não pode ser desfeita.`)) {
    return;
  }

  botao.disabled = true;
  try {
    const r = await apiFetch(`/usuarios/${id}`, { method: "DELETE" });
    if (r.status === 401) {
      window.location.href = "login.html";
      return;
    }
    if (!r.ok) {
      mostrar(erroDaApi(await r.json().catch(() => ({}))), false);
      return;
    }

    mostrar("Usuário excluído. O histórico foi preservado.", true);
    await carregar();
  } catch {
    mostrar("Sem conexão com o servidor.", false);
  } finally {
    botao.disabled = false;
  }
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
    botao.className = "button button-outline";
    const statusIcon = document.createElement("span");
    statusIcon.className = "material-symbols-outlined";
    statusIcon.setAttribute("aria-hidden", "true");
    statusIcon.textContent = u.ativo ? "person_off" : "person_check";
    botao.append(statusIcon, document.createTextNode(u.ativo ? "Desativar" : "Reativar"));
    botao.addEventListener("click", () => alterar(u.id, { ativo: !u.ativo }));
    acoes.append(botao);

    // A conta autenticada nunca recebe um botão de autoexclusão.
    if (usuarioAtual && u.id !== usuarioAtual.id) {
      const excluirBotao = document.createElement("button");
      excluirBotao.type = "button";
      excluirBotao.className = "button button-danger";
      const deleteIcon = document.createElement("span");
      deleteIcon.className = "material-symbols-outlined";
      deleteIcon.setAttribute("aria-hidden", "true");
      deleteIcon.textContent = "delete";
      excluirBotao.append(deleteIcon, document.createTextNode("Excluir"));
      excluirBotao.addEventListener("click", () => excluir(u.id, u.nome, excluirBotao));
      acoes.append(excluirBotao);
    }

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
    const r = await apiFetch("/usuarios", {
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
  usuarioAtual = u;
  carregar();
});
