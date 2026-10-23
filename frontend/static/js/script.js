/* ONG Solidária — front-end.
 * Usa a API Flask (/api/...). Se a API não existir (ex.: Cloudflare Pages,
 * que só hospeda arquivos estáticos), cai em "modo demo" com localStorage. */

const $ = (s) => document.querySelector(s);
const brl = (n) => Number(n).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const esc = (t) => { const d = document.createElement("div"); d.textContent = t ?? ""; return d.innerHTML; };

/* ---------- API real ---------- */
async function api(path, method = "GET", body) {
  let r;
  try {
    r = await fetch(path, {
      method, credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch { return { demo: true }; }
  if (!(r.headers.get("content-type") || "").includes("application/json")) return { demo: true };
  const data = await r.json();
  if (!r.ok) throw new Error(data.erro || "Erro inesperado.");
  return { data };
}

/* ---------- Modo demo (localStorage) ---------- */
const Demo = {
  load() {
    const d = JSON.parse(localStorage.getItem("ong_demo") || "null");
    return d || {
      usuarios: [], doacoes: [], sessao: null,
      projetos: [
        { id: 1, titulo: "Cesta Básica Solidária", descricao: "Distribuição mensal de cestas básicas.", meta: 5000 },
        { id: 2, titulo: "Reforço Escolar", descricao: "Aulas de reforço para crianças da comunidade.", meta: 3000 },
      ],
    };
  },
  save(d) { localStorage.setItem("ong_demo", JSON.stringify(d)); },
  run(path, method, body) {
    const d = this.load(); let out;
    const need = () => { if (!d.sessao) throw new Error("Faça login primeiro."); return d.sessao; };
    const total = (pid) => d.doacoes.filter((x) => x.projeto_id === pid).reduce((s, x) => s + x.valor, 0);
    if (path === "/api/usuarios/cadastro") {
      if (d.usuarios.some((u) => u.email === body.email.toLowerCase())) throw new Error("E-mail já cadastrado.");
      d.usuarios.push({ id: d.usuarios.length + 1, nome: body.nome, email: body.email.toLowerCase(), senha: body.senha });
      out = { ok: true };
    } else if (path === "/api/usuarios/login") {
      const u = d.usuarios.find((x) => x.email === body.email.toLowerCase() && x.senha === body.senha);
      if (!u) throw new Error("E-mail ou senha incorretos.");
      d.sessao = u.id; out = { id: u.id, nome: u.nome, email: u.email };
    } else if (path === "/api/usuarios/logout") { d.sessao = null; out = { ok: true }; }
    else if (path === "/api/usuarios/me") {
      const u = d.usuarios.find((x) => x.id === d.sessao);
      if (!u) throw new Error("Não autenticado.");
      out = { id: u.id, nome: u.nome, email: u.email };
    } else if (path === "/api/projetos" && method === "GET") {
      out = d.projetos.map((p) => ({ ...p, arrecadado: total(p.id) }));
    } else if (path === "/api/projetos") {
      need();
      d.projetos.push({ id: d.projetos.length + 1, titulo: body.titulo, descricao: body.descricao || "", meta: Number(body.meta) || 0 });
      out = { ok: true };
    } else if (path === "/api/doacoes" && method === "GET") {
      const uid = need();
      out = d.doacoes.filter((x) => x.usuario_id === uid).reverse()
        .map((x) => ({ ...x, projeto: d.projetos.find((p) => p.id === x.projeto_id)?.titulo }));
    } else if (path === "/api/doacoes") {
      const uid = need();
      if (!(Number(body.valor) > 0)) throw new Error("Valor inválido.");
      d.doacoes.push({ id: d.doacoes.length + 1, usuario_id: uid, projeto_id: Number(body.projeto_id), valor: Number(body.valor), criado_em: new Date().toISOString() });
      out = { ok: true };
    } else if (path === "/api/doacoes/resumo") {
      const uid = need(); const minhas = d.doacoes.filter((x) => x.usuario_id === uid);
      out = { minhas_doacoes: minhas.length, meu_total: minhas.reduce((s, x) => s + x.valor, 0), total_geral: d.doacoes.reduce((s, x) => s + x.valor, 0) };
    }
    this.save(d); return out;
  },
};

async function call(path, method = "GET", body) {
  const r = await api(path, method, body);
  if (r.demo) { $("#demoBadge").style.display = "inline-block"; return Demo.run(path, method, body); }
  return r.data;
}

/* ---------- Sessão / navegação ---------- */
async function usuarioAtual() { try { return await call("/api/usuarios/me"); } catch { return null; } }

async function iniciarNav() {
  const u = await usuarioAtual();
  if (u) {
    ["#navLogin", "#navCadastro"].forEach((s) => ($(s).style.display = "none"));
    $("#navSair").style.display = "inline";
    $("#navSair").onclick = async (e) => { e.preventDefault(); await call("/api/usuarios/logout", "POST"); location.href = "/"; };
  }
  return u;
}

function mostrar(el, texto, tipo) { el.textContent = texto; el.className = "msg " + tipo; }

/* ---------- Páginas ---------- */
const paginas = {
  async index() {
    const lista = await call("/api/projetos");
    $("#projetos").innerHTML = lista.map((p) => {
      const pct = p.meta ? Math.min(100, (p.arrecadado / p.meta) * 100) : 0;
      return `<article class="card"><h3>${esc(p.titulo)}</h3><p class="mut">${esc(p.descricao)}</p>
        <div class="barra"><div style="width:${pct}%"></div></div>
        <small>${brl(p.arrecadado)} de ${brl(p.meta)}</small></article>`;
    }).join("") || '<p class="mut">Nenhum projeto ainda.</p>';
  },

  login() {
    $("#formLogin").onsubmit = async (e) => {
      e.preventDefault();
      const f = Object.fromEntries(new FormData(e.target));
      try { await call("/api/usuarios/login", "POST", f); location.href = "/dashboard.html"; }
      catch (err) { mostrar($("#msg"), err.message, "erro"); }
    };
  },

  cadastro() {
    $("#formCadastro").onsubmit = async (e) => {
      e.preventDefault();
      const f = Object.fromEntries(new FormData(e.target));
      try {
        await call("/api/usuarios/cadastro", "POST", f);
        mostrar($("#msg"), "Conta criada! Redirecionando…", "ok");
        setTimeout(() => (location.href = "/login.html"), 800);
      } catch (err) { mostrar($("#msg"), err.message, "erro"); }
    };
  },

  async dashboard(user) {
    if (!user) { location.href = "/login.html"; return; }
    $("#ola").textContent = `Olá, ${user.nome}!`;

    const render = async () => {
      const [res, projs, minhas] = await Promise.all([
        call("/api/doacoes/resumo"), call("/api/projetos"), call("/api/doacoes"),
      ]);
      $("#stats").innerHTML = `
        <div class="card stat"><strong>${res.minhas_doacoes}</strong>minhas doações</div>
        <div class="card stat"><strong>${brl(res.meu_total)}</strong>meu total</div>
        <div class="card stat"><strong>${brl(res.total_geral)}</strong>total geral da ONG</div>`;
      $("#selProjeto").innerHTML = projs.map((p) => `<option value="${p.id}">${esc(p.titulo)}</option>`).join("");
      $("#listaDoacoes").innerHTML = minhas.map((d) =>
        `<li><span>${esc(d.projeto)}</span><strong>${brl(d.valor)}</strong></li>`).join("")
        || '<li class="mut">Você ainda não doou.</li>';
    };

    $("#formDoar").onsubmit = async (e) => {
      e.preventDefault();
      try { await call("/api/doacoes", "POST", Object.fromEntries(new FormData(e.target))); e.target.reset(); mostrar($("#msgDoar"), "Obrigado pela doação!", "ok"); render(); }
      catch (err) { mostrar($("#msgDoar"), err.message, "erro"); }
    };
    $("#formProjeto").onsubmit = async (e) => {
      e.preventDefault();
      try { await call("/api/projetos", "POST", Object.fromEntries(new FormData(e.target))); e.target.reset(); mostrar($("#msgProjeto"), "Projeto criado!", "ok"); render(); }
      catch (err) { mostrar($("#msgProjeto"), err.message, "erro"); }
    };
    render();
  },
};

document.addEventListener("DOMContentLoaded", async () => {
  const user = await iniciarNav();
  await paginas[document.body.dataset.page]?.(user);
});

