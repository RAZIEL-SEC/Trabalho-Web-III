import { useState } from 'react';
import { Outlet, Link, NavLink } from 'react-router';
import Logo from '../components/Logo';

const navLinks = [
  { to: '/', label: 'Início' },
  { to: '/quem-somos', label: 'Quem Somos' },
  { to: '/nossas-acoes', label: 'Nossas Ações' },
  { to: '/como-ajudar', label: 'Como Ajudar' },
  { to: '/contato', label: 'Contato' },
];

function Brand({ light = false }: { light?: boolean }) {
  return <Link to="/" className="brand" aria-label="Amigos do Zé Alguém, página inicial">
    <span className="brand-mark"><Logo size={36} /></span>
    <span className="brand-name" style={light ? { color: 'white' } : undefined}>Amigos do<br />Zé Alguém</span>
  </Link>;
}

export default function PublicLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const navClass = ({ isActive }: { isActive: boolean }) => isActive ? 'active' : undefined;

  return <div className="site-shell">
    <header className="site-header">
      <div className="site-container header-inner">
        <Brand />
        <nav className="site-nav" aria-label="Navegação principal">
          {navLinks.map(({ to, label }) => <NavLink key={to} to={to} end={to === '/'} className={navClass}>{label}</NavLink>)}
        </nav>
        <button className="menu-trigger" type="button" onClick={() => setMenuOpen(!menuOpen)} aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'} aria-expanded={menuOpen}>
          {menuOpen ? '✕' : '☰'}
        </button>
      </div>
      {menuOpen && <nav className="mobile-nav" aria-label="Navegação mobile">
        {navLinks.map(({ to, label }) => <NavLink key={to} to={to} end={to === '/'} className={navClass} onClick={() => setMenuOpen(false)}>{label}</NavLink>)}
      </nav>}
    </header>
    <main><Outlet /></main>
    <footer className="site-footer">
      <div className="site-container footer-inner">
        <div className="footer-grid">
          <div><Brand light /><p className="footer-copy" style={{ marginTop: 16 }}>Uma rede de pessoas que escolhe transformar cuidado em presença, alimento e dignidade.</p></div>
          <div><h3 className="footer-title">Navegação</h3><ul className="footer-list">{navLinks.map(({ to, label }) => <li key={to}><Link to={to}>{label}</Link></li>)}</ul></div>
          <div><h3 className="footer-title">Fale com a gente</h3><ul className="footer-list"><li>Informações de contato disponíveis em breve.</li><li><Link to="/contato">Acessar página de contato →</Link></li><li>Instagram · Facebook · WhatsApp</li></ul></div>
        </div>
        <div className="footer-bottom">© 2026 Amigos do Zé Alguém · Protótipo institucional</div>
      </div>
    </footer>
  </div>;
}
