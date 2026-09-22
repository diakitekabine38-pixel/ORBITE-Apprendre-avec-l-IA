import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { useCart } from "../cart";
import ThemeToggle from "./ThemeToggle";

const navLink = ({ isActive }) =>
  `px-3 py-2 text-sm rounded-lg transition ${isActive ? "text-brand bg-ivory-soft" : "text-muted hover:text-ink-deep"}`;

export default function Navbar() {
  const { user, logout } = useAuth();
  const { cartCount } = useCart();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-ivory/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
        <Link to="/" className="group flex shrink-0 items-center gap-2 font-display">
          <span className="flex h-9 w-9 items-center justify-center rounded-2xl border border-line bg-paper p-1 shadow-sm transition-all duration-300 group-hover:border-brand/60 group-active:scale-95">
            <img src="/logo.svg" alt="ORBITE" className="h-6 w-6 object-contain" />
          </span>
          <span className="text-lg font-semibold tracking-tight">ORBITE</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          <NavLink to="/catalogue" className={navLink}>Catalogue</NavLink>
          {user && <NavLink to="/dashboard" className={navLink}>Mon espace</NavLink>}
          {user && <NavLink to="/chat" className={navLink}>Coach IA</NavLink>}
          {user && (
            <NavLink
              to="/app/orbite"
              className={({ isActive }) =>
                `px-3 py-2 text-sm rounded-lg transition ${isActive ? "text-brand bg-ivory-soft" : "text-muted hover:text-ink-deep"}`
              }
            >
              🛰️ Mon Orbite
            </NavLink>
          )}
          {user && <NavLink to="/certificats" className={navLink}>Certificats</NavLink>}
          {["admin", "super_admin"].includes(user?.role) && (
            <NavLink to="/admin/agents" className={navLink}>Agents IA</NavLink>
          )}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          <ThemeToggle />
          {user ? (
            <>
              <Link
                to="/panier"
                className="relative rounded-xl !p-2 transition active:scale-90"
                aria-label="Mon panier"
                title="Mon panier"
              >
                <span className="block text-lg leading-none">🛒</span>
                {cartCount > 0 && (
                  <span className="animate-scale-in absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-glow px-1 text-[9px] font-bold text-white shadow-md">
                    {cartCount}
                  </span>
                )}
              </Link>
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