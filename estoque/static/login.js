const form = document.getElementById("form-login");
const email = document.getElementById("email");
const senha = document.getElementById("senha");
const erro = document.getElementById("erro");
const aviso = document.getElementById("aviso");
const caps = document.getElementById("caps");
const verSenha = document.getElementById("ver-senha");
const entrar = document.getElementById("entrar");

// Já tem sessão? Vai direto para o sistema.
fetch("/auth/eu")
  .then((r) => { if (r.ok) window.location.replace("itens.html"); })
  .catch(() => {});

// Veio de uma sessão que terminou (inatividade, senha trocada, "sair de todos").
if (new URLSearchParams(window.location.search).has("expirou")) {
  aviso.textContent = "Sua sessão terminou. Entre novamente.";
  aviso.hidden = false;
}

email.focus();

// Mostrar / ocultar senha
verSenha.addEventListener("click", () => {
  const mostrando = senha.type === "text";
  senha.type = mostrando ? "password" : "text";
  verSenha.textContent = mostrando ? "Mostrar" : "Ocultar";
  verSenha.setAttribute("aria-pressed", String(!mostrando));
  verSenha.setAttribute("aria-label", mostrando ? "Mostrar senha" : "Ocultar senha");
  senha.focus();
});

// Aviso de Caps Lock
function checarCaps(e) {
  caps.hidden = !(e.getModifierState && e.getModifierState("CapsLock"));
}
senha.addEventListener("keydown", checarCaps);
senha.addEventListener("keyup", checarCaps);
senha.addEventListener("blur", () => { caps.hidden = true; });

function limparErro() {
  erro.hidden = true;
  email.removeAttribute("aria-invalid");
  senha.removeAttribute("aria-invalid");
}
email.addEventListener("input", limparErro);
senha.addEventListener("input", limparErro);

function mostrarErro(texto, campo, marcar) {
  erro.textContent = texto;
  erro.hidden = false;
  if (marcar) marcar.forEach((c) => c.setAttribute("aria-invalid", "true"));
  if (campo) campo.focus();
}

function ocupado(sim) {
  entrar.disabled = sim;
  entrar.classList.toggle("carregando", sim);
  form.setAttribute("aria-busy", String(sim));
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  limparErro();
  aviso.hidden = true;

  if (!email.value.trim() || !email.checkValidity()) {
    mostrarErro("Informe um e-mail válido.", email, [email]);
    return;
  }
  if (!senha.value) {
    mostrarErro("Informe a senha.", senha, [senha]);
    return;
  }

  ocupado(true);
  try {
    const r = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email.value, senha: senha.value }),
    });

    if (r.ok) {
      window.location.href = "itens.html";
      return; // o botão fica em "carregando" até a página trocar
    }

    if (r.status === 429) {
      mostrarErro("Muitas tentativas. Aguarde alguns minutos e tente de novo.", null);
    } else if (r.status === 422) {
      mostrarErro("Confira o e-mail e a senha digitados.", email, [email]);
    } else {
      // 401: a API não diz se foi o e-mail ou a senha, e a tela também não
      mostrarErro("E-mail ou senha incorretos.", senha, [email, senha]);
      senha.select();
    }
    senha.value = "";
  } catch {
    mostrarErro("Sem conexão com o servidor. Verifique a internet e tente de novo.", null);
  }
  ocupado(false);
});
