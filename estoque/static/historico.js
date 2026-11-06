const corpo = document.getElementById("historico-lista");
const msg = document.getElementById("historico-msg");
const botaoLimpar = document.getElementById("historico-limpar");

function cell(texto) {
  const elemento = document.createElement("td");
  elemento.textContent = texto ?? "—";
  return elemento;
}

async function carregar() {
  corpo.innerHTML = '<tr><td colspan="6" class="empty">Carregando…</td></tr>';
  try {
    const resposta = await fetch("/movimentacoes?limite=200");
    if (resposta.status === 401) {
      location.href = "login.html";
      return;
    }
    if (!resposta.ok) throw new Error("Não foi possível consultar o histórico.");

    const dados = await resposta.json();
    corpo.replaceChildren();
    if (!dados.length) {
      const linha = document.createElement("tr");
      const celula = cell("Nenhuma movimentação registrada.");
      celula.colSpan = 6;
      celula.className = "empty";
      linha.append(celula);
      corpo.append(linha);
    }

    for (const movimentacao of dados) {
      const linha = document.createElement("tr");
      linha.append(
        cell(new Date(movimentacao.criado_em).toLocaleString("pt-BR")),
        cell(movimentacao.item_nome),
      );
      const tipo = cell("");
      const etiqueta = document.createElement("span");
      etiqueta.className = "pill " + movimentacao.tipo;
      etiqueta.textContent = movimentacao.tipo;
      tipo.append(etiqueta);
      linha.append(
        tipo,
        cell(Number(movimentacao.quantidade).toLocaleString("pt-BR", { minimumFractionDigits: 2 })),
        cell(movimentacao.usuario_id),
        cell(movimentacao.motivo || movimentacao.observacao),
      );
      corpo.append(linha);
    }
  } catch (erro) {
    msg.textContent = erro.message;
    msg.className = "feedback error";
  }
}

async function limparHistorico() {
  const confirmacao = window.prompt(
    "ATENÇÃO: isso apagará permanentemente todos os registros de movimentação. Os saldos atuais dos itens serão mantidos.\n\nDigite LIMPAR para confirmar:",
  );
  if (confirmacao !== "LIMPAR") return;

  botaoLimpar.disabled = true;
  msg.textContent = "Limpando histórico…";
  msg.className = "feedback";
  try {
    const resposta = await fetch("/movimentacoes/historico", { method: "DELETE" });
    if (resposta.status === 401) {
      location.href = "login.html";
      return;
    }
    if (resposta.status === 403) {
      throw new Error("Apenas administradores podem limpar o histórico.");
    }
    const dados = await resposta.json().catch(() => ({}));
    if (!resposta.ok) throw new Error(dados.detail || "Não foi possível limpar o histórico.");

    msg.textContent = `${dados.removidas} registro(s) removido(s). Os saldos atuais foram preservados.`;
    msg.className = "feedback success";
    await carregar();
  } catch (erro) {
    msg.textContent = erro.message;
    msg.className = "feedback error";
  } finally {
    botaoLimpar.disabled = false;
  }
}

document.getElementById("historico-atualizar").addEventListener("click", carregar);
if (botaoLimpar) botaoLimpar.addEventListener("click", limparHistorico);
carregar();
