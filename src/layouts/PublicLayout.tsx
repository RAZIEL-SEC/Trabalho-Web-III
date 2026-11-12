import { useEffect, useState } from "react"
import type { MouseEvent } from "react"
import { Outlet, Link, NavLink, useLocation } from "react-router"
import Logo from "../components/Logo"
import Icon from "../components/Icon"

const navLinks = [
  { to: "/", label: "Início" },
  { to: "/quem-somos", label: "Quem Somos" },
  { to: "/nossas-acoes", label: "Nossas Ações" },
  { to: "/como-ajudar", label: "Como Ajudar" },
  { to: "/contato", label: "Contato" },
]

function Brand({
  light = false,
  wide = false,
  iconOnly = false,
  onHomeClick,
}: {
  light?: boolean
  wide?: boolean
  iconOnly?: boolean
  onHomeClick?: (event: MouseEvent<HTMLAnchorElement>) => void
}) {
  return (
    <Link
      to="/"
      className={`brand${wide ? " brand--wide" : ""}`}
      aria-label="Amigos do Zé Alguém, página inicial"
      onClick={onHomeClick}
    >
      {iconOnly ? (
        <img
          className="brand-footer-logo"
          src="/images/amigos-do-ze-alguem-icon.svg"
          alt="Amigos do Zé Alguém"
        />
      ) : (
        <>
          <span className="brand-mobile-home-icon" aria-hidden="true">
            <img src="/images/amigos-do-ze-alguem-icon.svg" alt="" />
          </span>
          <span className="brand-compact">
            <span className="brand-mark">
              <Logo size={36} />
            </span>
            <span
              className="brand-name"
              style={light ? { color: "white" } : undefined}
            >
              Amigos do
              <br />
              Zé Alguém
            </span>
          </span>
          {wide && (
        <img
          className="brand-wide-logo"
          src="/images/amigos-do-ze-alguem-logo.svg"
          alt="Amigos do Zé Alguém"
        />
          )}
        </>
      )}
    </Link>
  )
}

export default function PublicLayout() {
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()
  const navClass = ({ isActive }: { isActive: boolean }) =>
    isActive ? "active" : undefined
  const handleBrandClick = (event: MouseEvent<HTMLAnchorElement>) => {
    if (location.pathname === "/" && !location.hash) {
      event.preventDefault()
      window.scrollTo({ top: 0, behavior: "smooth" })
    }
  }

  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      const target = location.hash
        ? document.getElementById(location.hash.slice(1))
        : null

      if (target) {
        target.scrollIntoView()
        return
      }

      window.scrollTo({ top: 0, left: 0, behavior: "auto" })
    })

    return () => cancelAnimationFrame(frame)
  }, [location.hash, location.pathname])

  return (
    <div className="site-shell">
      <header className="site-header">
        <div className="site-container header-inner">
        <Brand wide onHomeClick={handleBrandClick} />
          <nav className="site-nav" aria-label="Navegação principal">
            {navLinks.map(({ to, label }) => (
              <NavLink key={to} to={to} end={to === "/"} className={navClass}>
                {label}
              </NavLink>
            ))}
            <a href="https://amigosdozealguem.duckdns.org/estoque/login.html" className="nav-login">
              Entrar
            </a>
          </nav>
          <button
            className="menu-trigger"
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
            aria-expanded={menuOpen}
          >
            <Icon name={menuOpen ? "close" : "menu"} size={22} />
          </button>
        </div>
        {menuOpen && (
          <nav className="mobile-nav" aria-label="Navegação mobile">
            {navLinks.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={navClass}
                onClick={() => setMenuOpen(false)}
              >
                {label}
              </NavLink>
            ))}
            <a
              href="https://amigosdozealguem.duckdns.org/estoque/login.html"
              className="nav-login"
              onClick={() => setMenuOpen(false)}
            >
              Entrar
            </a>
          </nav>
        )}
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="site-footer">
        <div className="site-container footer-inner">
          <div className="footer-grid">
            <div>
              <Brand light iconOnly onHomeClick={handleBrandClick} />
              <p className="footer-copy" style={{ marginTop: 16 }}>
                Uma rede de pessoas que escolhe transformar cuidado em presença,
                alimento e dignidade.
              </p>
            </div>
            <div>
              <h3 className="footer-title">Navegação</h3>
              <ul className="footer-list">
                {navLinks.map(({ to, label }) => (
                  <li key={to}>
                    <Link to={to}>{label}</Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="footer-title">Fale com a gente</h3>
              <ul className="footer-list">
                <li>
                  <a href="mailto:contato@amigosdozealgem.org.br">
                    contato@amigosdozealgem.org.br
                  </a>
                </li>
                <li>
                  <a href="tel:+5521996801996">+55 (21) 99680-1996</a>
                </li>
                <li>
                  <a
                    href="https://www.instagram.com/amigosdozealguem/"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Instagram
                  </a>{" "}
                  ·{" "}
                  <a
                    href="https://www.facebook.com/AmigosDoZeAlguem"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Facebook
                  </a>{" "}
                  ·{" "}
                  <a
                    href="https://wa.me/5521996801996"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    WhatsApp
                  </a>
                </li>
                <li>
                  <Link to="/contato">Acessar página de contato →</Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            © 2026 Amigos do Zé Alguém · Website institucional
          </div>
        </div>
      </footer>
    </div>
  )
}
