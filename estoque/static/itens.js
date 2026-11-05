const form=document.getElementById("form-item"),msg=document.getElementById("item-msg"),corpo=document.getElementById("itens-lista");
function cell(t){const e=document.createElement("td");e.textContent=t??"—";return e}
function feedback(t,s="success"){msg.textContent=t;msg.className="feedback "+s}
async function carregar(){
  corpo.innerHTML='<tr><td colspan="5" class="empty">Carregando…</td></tr>';
  try{
    const r=await fetch("/itens?limite=200");
    if(r.status===401){location.href="login.html";return}
    if(!r.ok)throw Error("Falha ao consultar itens.");
    const itens=await r.json();corpo.replaceChildren();
    if(!itens.length){const tr=document.createElement("tr"),td=cell("Nenhum item ativo cadastrado.");td.colSpan=5;td.className="empty";tr.append(td);corpo.append(tr);return}
    for(const i of itens){
      const tr=document.createElement("tr");
      tr.append(cell(i.nome),cell(i.unidade),cell(Number(i.saldo).toLocaleString("pt-BR",{minimumFractionDigits:2})));
      const situacao=cell(""),tag=document.createElement("span");tag.className="pill ativo";tag.textContent="Ativo";situacao.append(tag);tr.append(situacao);
      const acoes=cell(""),botao=document.createElement("button");botao.type="button";botao.className="button button-danger";botao.textContent="Excluir";botao.setAttribute("aria-label",`Excluir ${i.nome}`);
      botao.addEventListener("click",()=>excluir(i,botao));acoes.append(botao);tr.append(acoes);corpo.append(tr);
    }
  }catch(e){feedback(e.message,"error")}
}
async function excluir(item,botao){
  const ok=window.confirm(`Deseja excluir "${item.nome}"? O item sairá da lista ativa, mas o histórico de movimentações será preservado.`);
  if(!ok)return;
  botao.disabled=true;
  try{
    const r=await fetch(`/itens/${item.id}`,{method:"DELETE"});
    const d=await r.json().catch(()=>({}));
    if(r.status===401){location.href="login.html";return}
    if(!r.ok)throw Error(typeof d.detail==="string"?d.detail:"Não foi possível excluir o item.");
    feedback(`Item "${item.nome}" excluído. O histórico foi preservado.`);
    await carregar();
  }catch(e){feedback(e.message,"error");botao.disabled=false}
}
form.addEventListener("submit",async e=>{
  e.preventDefault();const b=form.querySelector('button[type="submit"]');b.disabled=true;
  try{
    const r=await fetch("/itens",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.fromEntries(new FormData(form)))});
    const d=await r.json().catch(()=>({}));
    if(r.status===401){location.href="login.html";return}
    if(!r.ok)throw Error(typeof d.detail==="string"?d.detail:"Confira os dados informados.");
    form.reset();feedback("Item cadastrado com sucesso.");await carregar();
  }catch(e){feedback(e.message,"error")}finally{b.disabled=false}
});
document.getElementById("atualizar-itens").addEventListener("click",carregar);carregar();