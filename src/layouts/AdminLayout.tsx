import { useState } from 'react';
import { Outlet, NavLink, Link, useNavigate } from 'react-router';
import Logo from '../components/Logo';
import { USUARIO_LOGADO } from '../data/mockData';

const navItems = [
  { to: '/admin/dashboard', label: 'Painel', icon: '▦', end: true },
  { to: '/admin/dashboard/movimentacoes', label: 'Movimentações', icon: '≡', end: false },
  { to: '/admin/dashboard/registrar', label: 'Registrar', icon: '+', end: false },
];

function AdminBrand() {
  return <Link to="/" className="admin-brand"><span className="brand-mark"><Logo size={32} /></span><span className="brand-name">Amigos do<br />Zé Alguém</span></Link>;
}

export default function AdminLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const navClass = ({ isActive }: { isActive: boolean }) => isActive ? 'active' : undefined;
  const links = <>{navItems.map(({ to, label, icon, end }) => <NavLink key={to} to={to} end={end} className={navClass} onClick={() => setMenuOpen(false)}><span aria-hidden="true">{icon}</span>{label}</NavLink>)}</>;
  return <div className="admin-shell">
    <aside className="admin-sidebar"><AdminBrand /><p className="admin-subtitle">Área administrativa</p><nav className="admin-nav" aria-label="Navegação administrativa">{links}</nav><div className="admin-user"><small>Conectada como</small><strong>{USUARIO_LOGADO.nome}</strong><button type="button" onClick={() => navigate('/admin')}>Sair da área administrativa →</button></div></aside>
    <div className="admin-main">
      <header className="admin-mobile-header"><AdminBrand /><button className="menu-trigger" type="button" onClick={() => setMenuOpen(!menuOpen)} aria-expanded={menuOpen} aria-label="Abrir navegação">{menuOpen ? '✕' : '☰'}</button></header>
      {menuOpen && <nav className="admin-nav" style={{ background: '#102f5b' }} aria-label="Navegação administrativa mobile">{links}<button type="button" onClick={() => navigate('/admin')} style={{ margin: '8px 13px', color: '#c0d8ed', background: 'none', border: 0 }}>Sair</button></nav>}
      <main className="admin-content"><Outlet /></main>
    </div>
  </div>;
}
