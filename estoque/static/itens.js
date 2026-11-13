const form=document.getElementById("form-item"),msg=document.getElementById("item-msg"),corpo=document.getElementById("itens-lista");
const grupoSelect=document.getElementById("item-grupo"),subgrupoSelect=document.getElementById("item-subgrupo");
const filtroGrupo=document.getElementById("filtro-grupo"),filtroSubgrupo=document.getElementById("filtro-subgrupo");
const busca=document.getElementById("busca-itens"),ordenacao=document.getElementById("ordenar-itens");
const rotulosUnidade={"kg":"Quilograma (kg)","g":"Grama (g)","un":"Unidade (un)","l":"Litro (L)","ml":"Mililitro (ml)","pacote":"Pacote","garrafa":"Garrafa","frasco":"Frasco","lata":"Lata","caixa":"Caixa","fardo":"Fardo","kit":"Kit","par":"Par","rolo":"Rolo","duzia":"Dúzia","bandeja":"Bandeja","saco":"Saco","galao":"Galão"};
let grupos=[],subgrupos=[],itensCache=[];
function nomeUnidade(codigo){return rotulosUnidade[codigo]||codigo||"—"}
function cell(t){const e=document.createElement("td");e.textContent=t??"—";return e}
function feedback(t,s="success"){msg.textContent=t;msg.className="feedback "+s}
async function buscarApi(url){const r=await fetch(url);if(r.status===401){location.href="/estoque/login";throw Error("Sessão expirada.")}if(!r.ok)throw Error("Falha ao consultar "+url);return r.json()}
function subgruposDoGrupo(id){return subgrupos.filter(s=>s.grupo_id===Number(id)&&s.nome!=="Sem subgrupo")}
async function carregarClassificacoes(){
 [grupos,subgrupos]=await Promise.all([buscarApi("/classificacoes/grupos"),buscarApi("/classificacoes/subgrupos")]);
 grupoSelect.replaceChildren(new Option("Selecione o grupo",""));filtroGrupo.replaceChildren(new Option("Todos os grupos",""));
 grupos.forEach(g=>{grupoSelect.add(new Option(g.nome,g.id));filtroGrupo.add(new Option(g.nome,g.id))});
 atualizarSubgrupos();atualizarFiltroSubgrupos();
}
function atualizarSubgrupos(){
 const id=Number(grupoSelect.value),lista=subgruposDoGrupo(id);
 subgrupoSelect.replaceChildren(new Option("Classificar diretamente no grupo","grupo"));\n lista.forEach(s=>subgrupoSelect.add(new Option(s.nome,String(s.id))));\n subgrupoSelect.disabled=!id;subgrupoSelect.required=false;
}
function atualizarFiltroSubgrupos(){
 const id=Number(filtroGrupo.value);filtroSubgrupo.replaceChildren(new Option("Todos os subgrupos",""));
 subgrupos.filter(s=>s.nome!=="Sem subgrupo"&&(!id||s.grupo_id===id)).forEach(s=>filtroSubgrupo.add(new Option(s.nome,s.id)));
 renderizarItens();
}
function dadosClassificacao(item){const s=subgrupos.find(x=>x.id===item.subgrupo_id),g=grupos.find(x=>x.id===s?.grupo_id);return {s,g,grupo:g?.nome||"—",subgrupo:s?.nome==="Sem subgrupo"?"—":(s?.nome||"—")}}
function renderizarItens(){
 const grupoId=Number(filtroGrupo.value),subgrupoId=Number(filtroSubgrupo.value),termo=(busca.value||"").trim().toLocaleLowerCase("pt-BR");
 let itens=itensCache.filter(i=>{const c=dadosClassificacao(i);return (!subgrupoId||i.subgrupo_id===subgrupoId)&&(!grupoId||c.g?.id===grupoId)&&(!termo||[i.nome,c.grupo,c.subgrupo,nomeUnidade(i.unidade)].some(v=>String(v).toLocaleLowerCase("pt-BR").includes(termo)))});
 const [campo,direcao]=(ordenacao.value||"nome-asc").split("-"),fator=direcao==="desc"?-1:1;
 itens.sort((a,b)=>{let av,bv;if(campo==="saldo"){av=Number(a.saldo);bv=Number(b.saldo)}else if(campo==="data"){av=new Date(a.criado_em||0).getTime();bv=new Date(b.criado_em||0).getTime()}else{av=String(a.nome||"");bv=String(b.nome||"")}return (typeof av==="string"?av.localeCompare(bv,"pt-BR",{sensitivity:"base"}):av-bv)*fator});
 corpo.replaceChildren();
 if(!itens.length){const tr=document.createElement("tr"),td=cell(itensCache.length?"Nenhum item corresponde à pesquisa ou aos filtros.":"Nenhum item ativo cadastrado.");td.colSpan=8;td.className="empty";tr.append(td);corpo.append(tr);return}
 for(const i of itens){
  const c=dadosClassificacao(i),tr=document.createElement("tr");
  tr.append(cell(i.nome),cell(c.grupo),cell(c.subgrupo),cell(nomeUnidade(i.unidade)),cell(Number(i.saldo).toLocaleString("pt-BR",{minimumFractionDigits:2})),cell(i.criado_em?new Date(i.criado_em).toLocaleDateString("pt-BR"):"—"));
  const situacao=cell(""),tag=document.createElement("span");tag.className="pill ativo";tag.textContent="Ativo";situacao.append(tag);tr.append(situacao);
  const acoes=cell(""),seletor=document.createElement("select");seletor.setAttribute("aria-label",`Classificação de ${i.nome}`);
  grupos.forEach(g=>{seletor.add(new Option(g.nome+" (somente grupo)", "grupo:"+g.id));subgruposDoGrupo(g.id).forEach(s=>seletor.add(new Option(g.nome+" / "+s.nome,"subgrupo:"+s.id)))});
  const atualSub=c.s?.nome==="Sem subgrupo"?"grupo:"+c.g?.id:"subgrupo:"+i.subgrupo_id;seletor.value=atualSub;
  const salvar=document.createElement("button");salvar.type="button";salvar.className="button button-outline";salvar.textContent="Salvar classificação";
  salvar.addEventListener("click",async()=>{salvar.disabled=true;try{const [tipo,id]=seletor.value.split(":");const payload=tipo==="grupo"?{grupo_id:Number(id)}:{subgrupo_id:Number(id)};const resp=await apiFetch(`/itens/${i.id}/classificacao`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}),d=await resp.json().catch(()=>({}));if(!resp.ok)throw Error(typeof d.detail==="string"?d.detail:"Não foi possível reclassificar.");feedback(`Classificação de "${i.nome}" atualizada.`);await carregar()}catch(e){feedback(e.message,"error");salvar.disabled=false}});
  const botao=document.createElement("button");botao.type="button";botao.className="button button-danger";botao.textContent="Excluir";botao.setAttribute("aria-label",`Excluir ${i.nome}`);botao.addEventListener("click",()=>excluir(i,botao));acoes.append(seletor,salvar,botao);tr.append(acoes);corpo.append(tr);
 }
}
async function carregar(){corpo.innerHTML='<tr><td colspan="8" class="empty">Carregando…</td></tr>';try{itensCache=await buscarApi("/itens?limite=200");renderizarItens()}catch(e){feedback(e.message,"error")}}
async function excluir(item,botao){
 if(!confirm(`Deseja excluir "${item.nome}"? O histórico de movimentações será preservado.`))return;botao.disabled=true;
 try{const r=await apiFetch(`/itens/${item.id}`,{method:"DELETE"}),d=await r.json().catch(()=>({}));if(r.status===401){location.href="/estoque/login";return}if(!r.ok)throw Error(typeof d.detail==="string"?d.detail:"Não foi possível excluir o item.");feedback(`Item "${item.nome}" excluído. O histórico foi preservado.`);await carregar()}catch(e){feedback(e.message,"error");botao.disabled=false}
}
grupoSelect.addEventListener("change",atualizarSubgrupos);filtroGrupo.addEventListener("change",atualizarFiltroSubgrupos);filtroSubgrupo.addEventListener("change",renderizarItens);busca.addEventListener("input",renderizarItens);ordenacao.addEventListener("change",renderizarItens);
form.addEventListener("submit",async e=>{
 e.preventDefault();const b=form.querySelector('button[type="submit"]');b.disabled=true;
 try{const dados=Object.fromEntries(new FormData(form));const grupoId=Number(grupoSelect.value);dados.grupo_id=grupoId;if(dados.subgrupo_id==="grupo"||!dados.subgrupo_id)delete dados.subgrupo_id;else dados.subgrupo_id=Number(dados.subgrupo_id);
  const r=await apiFetch("/itens",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(dados)}),d=await r.json().catch(()=>({}));if(r.status===401){location.href="/estoque/login";return}if(!r.ok)throw Error(typeof d.detail==="string"?d.detail:"Confira os dados informados.");
  form.reset();atualizarSubgrupos();feedback("Item cadastrado com sucesso.");await carregarClassificacoes();await carregar();
 }catch(e){feedback(e.message,"error")}finally{b.disabled=false}
});
document.getElementById("atualizar-itens").addEventListener("click",async()=>{await carregarClassificacoes();await carregar()});
(async()=>{try{await carregarClassificacoes();await carregar()}catch(e){feedback(e.message,"error")}})();
