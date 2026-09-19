import { Link } from 'react-router';

const acoes = [
  { icon: '🍱', titulo: 'Quentinhas', desc: 'Refeições preparadas com escuta, respeito e presença.' },
  { icon: '🛒', titulo: 'Cestas básicas', desc: 'Alimentos essenciais para famílias em vulnerabilidade.' },
  { icon: '🧴', titulo: 'Kits de higiene', desc: 'Cuidado que começa pelos itens mais cotidianos.' },
  { icon: '📚', titulo: 'Amigos da Escola', desc: 'Apoio à alfabetização e às trajetórias de crianças.' },
];
const valores = ['Humanização', 'Geração de Renda', 'Cidadania', 'Vínculo Familiar', 'Direito à Moradia Digna', 'Acesso à Saúde', 'Segurança Alimentar', 'Conscientização', 'Direito à Educação'];

export default function Home() {
  return <>
    <section className="home-hero">
      <div className="site-container hero-inner"><div className="hero-copy">
        <p className="eyebrow">Organização sem fins lucrativos</p>
        <h1 className="hero-title">Combater a fome é <em>aproximar pessoas.</em></h1>
        <p className="hero-text">Somos uma rede de voluntários e parceiros que transforma solidariedade em alimento, cuidado e novas possibilidades para a comunidade.</p>
        <div className="button-row"><Link to="/como-ajudar" className="button-primary">Como ajudar <span aria-hidden="true">→</span></Link><Link to="/nossas-acoes" className="button-secondary">Conheça nossas ações</Link></div>
      </div></div>
    </section>
    <section className="intro-section"><div className="site-container intro-grid">
      <div><p className="section-kicker">A nossa missão</p><h2 className="section-title">Mais do que alimento, oferecemos caminhos para a dignidade.</h2><p className="section-text">Acreditamos que ninguém deve passar fome. Por isso, atuamos lado a lado com as comunidades, unindo ações de alimentação, educação, saúde e fortalecimento de vínculos.</p><Link className="text-link" to="/quem-somos">Conheça a nossa história <span aria-hidden="true">→</span></Link></div>
      <div className="mission-photo"><img src="https://images.unsplash.com/photo-1593113630400-ea4288922497?w=850&h=620&fit=crop&auto=format" alt="Voluntários organizando alimentos para a distribuição" /><div className="mission-tag">Cuidado em rede, todos os dias.</div></div>
    </div></section>
    <section className="actions-section"><div className="site-container">
      <div className="section-heading"><div><p className="section-kicker">Onde a ajuda acontece</p><h2 className="section-title">Ações que chegam perto de quem precisa.</h2></div><Link className="text-link" to="/nossas-acoes">Ver todas as ações →</Link></div>
      <div className="action-grid">{acoes.map((acao) => <article className="action-card" key={acao.titulo}><div className="action-icon" aria-hidden="true">{acao.icon}</div><h3>{acao.titulo}</h3><p>{acao.desc}</p></article>)}</div>
    </div></section>
    <section className="values-section"><div className="site-container"><p className="section-kicker">Nossa mandala social</p><h2 className="section-title">Nove valores. Uma mesma direção.</h2><p className="section-text" style={{ maxWidth: 620 }}>Cada decisão é orientada por valores que reconhecem as pessoas por inteiro — suas necessidades, histórias e potências.</p><div className="values-grid">{valores.map((valor, index) => <div className="value-pill" key={valor}><span className="value-number">{index + 1}</span>{valor}</div>)}</div></div></section>
    <section className="community-cta"><div className="site-container cta-box"><div><p className="eyebrow">Uma comunidade mais forte começa aqui</p><h2 className="section-title">O seu gesto pode abrir espaço para novos começos.</h2><p className="section-text">Doe, seja voluntário ou aproxime a sua organização. Há muitas formas de caminhar com a gente.</p></div><Link to="/como-ajudar" className="button-primary">Quero fazer parte</Link></div></section>
  </>;
}
