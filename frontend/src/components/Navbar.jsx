import { Link, NavLink, useNavigate } from "react-router-dom";
import { ShoppingCart } from "lucide-react";
import { useAuth } from "../auth";
import { useCart } from "../cart";
import { publicNavLinks } from "../navigation";
import ThemeToggle from "./ThemeToggle";
import Brand from "./Brand";
import NotificationBell from "./NotificationBell";

const navLink = ({ isActive }) =>
  `px-3 py-2 text-sm rounded-lg transition ${isActive ? "text-brand bg-ivory-soft" : "text-muted hover:text-ink-deep"}`;

export default function Navbar() {
  const { user, logout } = useAuth();
  const { cartCount } = useCart();
  const navigate = useNavigate();

  const links = publicNavLinks(user);

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-ivory/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
        <Brand />

        <nav className="hidden items-center gap-1 md:flex">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} className={navLink}>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          <ThemeToggle />
          {user ? (
            <>
              <NotificationBell />
              {user.role === "student" && (
                <Link
                  to="/student/panier"
                  className="relative rounded-xl !p-2 transition active:scale-90"
                  aria-label="Mon panier"
                  title="Mon panier"
                >
                  <ShoppingCart className="h-5 w-5" />
                  {cartCount > 0 && (
                    <span className="animate-scale-in absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-glow px-1 text-[9px] font-bold text-white shadow-md">
                      {cartCount}
                    </span>
                  )}
                </Link>
              )}
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