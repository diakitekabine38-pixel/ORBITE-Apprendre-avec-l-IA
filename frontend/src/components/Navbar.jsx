import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import ThemeToggle from "./ThemeToggle";

function Orbits() {
  return (
    <svg width="34" height="34" viewBox="0 0 34 34" fill="none" aria-hidden>
      <circle cx="17" cy="17" r="4" fill="#7C3AED" />
      <ellipse cx="17" cy="17" rx="14" ry="5.5" stroke="#8B5CF6" strokeWidth="1.5" transform="rotate(-18 17 17)" />
      <ellipse cx="17" cy="17" rx="14" ry="5.5" stroke="#A78BFA" strokeWidth="1.5" opacity=".5" transform="rotate(45 17 17)" />
    </svg>
  );
}

const navLink = ({ isActive }) =>
  `px-3 py-2 text-sm rounded-lg transition ${isActive ? "text-brand bg-ivory-soft" : "text-muted hover:text-ink-deep"}`;

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-ivory/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-700">
          <Orbits />
          <span className="font-semibold tracking-tight">
            ORBITE
          </span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          <NavLink to="/catalogue" className={navLink}>Catalogue</NavLink>
          {user && <NavLink to="/dashboard" className={navLink}>Mon espace</NavLink>}
          {user && <NavLink to="/chat" className={navLink}>Coach IA</NavLink>}
          {user && <NavLink to="/certificats" className={navLink}>Certificats</NavLink>}
          {["admin", "super_admin"].includes(user?.role) && (
            <NavLink to="/admin/agents" className={navLink}>Agents IA</NavLink>
          )}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          <ThemeToggle />
          {user ? (
            <>
              <Link to="/panier" className="btn-ghost !px-3 !py-2" aria-label="Panier">🛒</Link>
              <span className="hidden text-sm text-muted sm:block">
                {user.first_name || user.username}
                <span className="ml-2 rounded-full bg-brand/15 px-2 py-0.5 text-xs text-brand">
                  Nv.{user.level} · {user.xp} XP
                </span>
              </span>
              <button
                onClick={() => {
                  logout();
                  navigate("/");
                }}
                className="btn-ghost !px-4"
              >
                Déconnexion
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-ghost !px-4">Connexion</Link>
              <Link to="/inscription" className="btn-primary !px-4">Créer un compte</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}