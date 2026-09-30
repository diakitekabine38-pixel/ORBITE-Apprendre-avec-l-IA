import { useState } from "react";
import { NavLink } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { cn } from "./cn";

const linkCls = ({ isActive }) =>
  cn(
    "rounded-lg px-3 py-2 text-sm transition-colors",
    isActive ? "bg-ivory-soft font-medium text-brand" : "text-muted hover:text-ink-deep",
  );

export default function Navbar({ brand, links = [], actions, className }) {
  const [open, setOpen] = useState(false);

  const renderLink = (link, onNavigate) => {
    const close = () => onNavigate?.();
    if (link.to) {
      return (
        <NavLink key={link.to} to={link.to} end={link.end} className={linkCls} onClick={close}>
          {link.label}
        </NavLink>
      );
    }
    return (
      <button
        key={link.label}
        type="button"
        onClick={() => {
          close();
          link.onClick?.();
        }}
        className="rounded-lg px-3 py-2 text-left text-sm text-muted transition-colors hover:text-ink-deep"
      >
        {link.label}
      </button>
    );
  };

  return (
    <header className={cn("sticky top-0 z-40 border-b border-line bg-ivory/85 backdrop-blur", className)}>
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
        {brand}
        <nav className="hidden items-center gap-1 md:flex">
          {links.map((link) => renderLink(link))}
        </nav>
        <div className="ml-auto flex items-center gap-3">
          {actions}
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-line bg-paper text-ink-deep md:hidden"
            aria-label={open ? "Fermer le menu" : "Ouvrir le menu"}
          >
            {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>
      {open && (
        <div className="animate-scale-in mx-auto flex max-w-6xl flex-col gap-1 border-t border-line px-4 py-3 md:hidden">
          {links.map((link) => renderLink(link, () => setOpen(false)))}
        </div>
      )}
    </header>
  );
}