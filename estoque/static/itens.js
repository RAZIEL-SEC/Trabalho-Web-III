const form=document.getElementById("form-item"),msg=document.getElementById("item-msg"),corpo=document.getElementById("itens-lista");
const grupoSelect=document.getElementById("item-grupo"),subgrupoSelect=document.getElementById("item-subgrupo");
const filtroGrupo=document.getElementById("filtro-grupo"),filtroSubgrupo=document.getElementById("filtro-subgrupo");
const rotulosUnidade={"kg":"Quilograma (kg)","g":"Grama (g)","un":"Unidade (un)","l":"Litro (L)","ml":"Mililitro (ml)","pacote":"Pacote","garrafa":"Garrafa","frasco":"Frasco","lata":"Lata","caixa":"Caixa","fardo":"Fardo","kit":"Kit","par":"Par","rolo":"Rolo","duzia":"Dúzia","bandeja":"Bandeja","saco":"Saco","galao":"Galão"};
let grupos=[],subgrupos=[],itensCache=[];
function nomeUnidade(codigo){return rotulosUnidade[codigo]||codigo||"—"}
function cell(t){const e=document.createElement("td");e.textContent=t??"—";return e}
function feedback(t,s="success"){msg.textContent=t;msg.className="feedback "+s}
async function buscar(url){const r=await fetch(url);if(r.status===401){location.href="/estoque/login";throw Error("Sessão expirada.")}if(!r.ok)throw Error("Falha ao consultar "+url);return r.json()}
async function carregarClassificacoes(){
 [grupos,subgrupos]=await Promise.all([buscar("/classificacoes/grupos"),buscar("/classificacoes/subgrupos")]);
 grupoSelect.replaceChildren(new Option("Selecione o grupo",""));filtroGrupo.replaceChildren(new Option("Todos os grupos",""));
 grupos.forEach(g=>{grupoSelect.add(new Option(g.nome,g.id));filtroGrupo.add(new Option(g.nome,g.id))});
 atualizarSubgrupos();atualizarFiltroSubgrupos();
}
function atualizarSubgrupos(){const id=Number(grupoSelect.value);subgrupoSelect.replaceChildren(new Option("Selecione o subgrupo",""));subgrupos.filter(s=>s.grupo_id===id).forEach(s=>subgrupoSelect.add(new Option(s.nome,s.id)));subgrupoSelect.disabled=!id}
function atualizarFiltroSubgrupos(){const id=Number(filtroGrupo.value);filtroSubgrupo.replaceChildren(new Option("Todos os subgrupos",""));subgrupos.filter(s=>!id||s.grupo_id===id).forEach(s=>filtroSubgrupo.add(new Option(s.nome,s.id)));renderizarItens()}
function renderizarItens(){
 const grupoId=Number(filtroGrupo.value),subgrupoId=Number(filtroSubgrupo.value);
 const itens=itensCache.filter(i=>{const s=subgrupos.find(x=>x.id===i.subgrupo_id);return (!subgrupoId||i.subgrupo_id===subgrupoId)&&(!grupoId||s?.grupo_id===grupoId)});
 corpo.replaceChildren();
 if(!itens.length){const tr=document.createElement("tr"),td=cell(itensCache.length?"Nenhum item corresponde aos filtros.":"Nenhum item ativo cadastrado.");td.colSpan=7;td.className="empty";tr.append(td);corpo.append(tr);return}
 for(const i of itens){
  const s=subgrupos.find(x=>x.id===i.subgrupo_id),g=grupos.find(x=>x.id===s?.grupo_id),tr=document.createElement("tr");
  tr.append(cell(i.nome),cell(g?.nome||"—"),cell(s?.nome||"—"),cell(nomeUnidade(i.unidade)),cell(Number(i.saldo).toLocaleString("pt-BR",{minimumFractionDigits:2})));
  const situacao=cell(""),tag=document.createElement("span");tag.className="pill ativo";tag.textContent="Ativo";situacao.append(tag);tr.append(situacao);
  const acoes=cell(""),seletor=document.createElement("select");seletor.setAttribute("aria-label",`Subgrupo de ${i.nome}`);subgrupos.filter(x=>grupos.some(g=>g.id===x.grupo_id)).forEach(x=>seletor.add(new Option((grupos.find(g=>g.id===x.grupo_id)?.nome||"")+" / "+x.nome,x.id)));seletor.value=String(i.subgrupo_id);const salvar=document.createElement("button");salvar.type="button";salvar.className="button button-outline";salvar.textContent="Salvar classificação";salvar.addEventListener("click",async()=>{salvar.disabled=true;try{const resp=await apiFetch(`/itens/${i.id}/classificacao`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({subgrupo_id:Number(seletor.value)})}),d=await resp.json().catch(()=>({}));if(!resp.ok)throw Error(typeof d.detail==="string"?d.detail:"Não foi possível reclassificar.");feedback(`Classificação de "${i.nome}" atualizada.`);await carregar()}catch(e){feedback(e.message,"error");salvar.disabled=false}});const botao=document.createElement("button");botao.type="button";botao.className="button button-danger";botao.textContent="Excluir";botao.setAttribute("aria-label",`Excluir ${i.nome}`);botao.addEventListener("click",()=>excluir(i,botao));acoes.append(seletor,salvar,botao);tr.append(acoes);corpo.append(tr);
 }
}
async function carregar(){corpo.innerHTML='<tr><td colspan="7" class="empty">Carregando…</td></tr>';try{itensCache=await buscar("/itens?limite=200");renderizarItens()}catch(e){feedback(e.message,"error")}}
async function excluir(item,botao){
 if(!confirm(`Deseja excluir "${item.nome}"? O histórico de movimentações será preservado.`))return;botao.disabled=true;
 try{const r=await apiFetch(`/itens/${item.id}`,{method:"DELETE"}),d=await r.json().catch(()=>({}));if(r.status===401){location.href="/estoque/login";return}if(!r.ok)throw Error(typeof d.detail==="string"?d.detail:"Não foi possível excluir o item.");feedback(`Item "${item.nome}" excluído. O histórico foi preservado.`);await carregar()}catch(e){feedback(e.message,"error");botao.disabled=false}
}
grupoSelect.addEventListener("change",atualizarSubgrupos);filtroGrupo.addEventListener("change",atualizarFiltroSubgrupos);filtroSubgrupo.addEventListener("change",renderizarItens);
form.addEventListener("submit",async e=>{e.preventDefault();const b=form.querySelector('button[type="submit"]');b.disabled=true;try{const dados=Object.fromEntries(new FormData(form));dados.subgrupo_id=Number(dados.subgrupo_id);const r=await apiFetch("/itens",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(dados)}),d=await r.json().catch(()=>({}));if(r.status===401){location.href="/estoque/login";return}if(!r.ok)throw Error(typeof d.detail==="string"?d.detail:"Confira os dados informados.");form.reset();atualizarSubgrupos();feedback("Item cadastrado com sucesso.");await carregar()}catch(e){feedback(e.message,"error")}finally{b.disabled=false}});
document.getElementById("atualizar-itens").addEventListener("click",async()=>{await carregarClassificacoes();await carregar()});
(async()=>{try{await carregarClassificacoes();await carregar()}catch(e){feedback(e.message,"error")}})();
