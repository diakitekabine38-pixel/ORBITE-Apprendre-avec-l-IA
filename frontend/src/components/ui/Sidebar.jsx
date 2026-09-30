import { NavLink } from "react-router-dom";
import { cn } from "./cn";

function renderItem(item) {
  const cls = ({ isActive }) =>
    cn(
      "flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors",
      isActive || item.active
        ? "bg-orbital-50 font-medium text-orbital-700"
        : "text-ink-soft hover:bg-ivory-soft hover:text-ink-deep",
    );

  const inner = (
    <>
      {item.icon && <item.icon className="h-4 w-4 shrink-0" />}
      <span className="flex-1 truncate">{item.label}</span>
      {typeof item.badge === "number" && item.badge > 0 && (
        <span className="rounded-full bg-brand px-2 py-0.5 text-[10px] font-bold text-white">
          {item.badge}
        </span>
      )}
      {item.endIcon && <item.endIcon className="h-4 w-4 shrink-0 text-muted" />}
    </>
  );

  if (item.to) {
    return (
      <NavLink key={item.key ?? item.to} to={item.to} end={item.end} className={cls}>
        {inner}
      </NavLink>
    );
  }

  return (
    <button
      key={item.key ?? item.label}
      type="button"
      onClick={item.onClick}
      className={cls({ isActive: item.active })}
    >
      {inner}
    </button>
  );
}

export default function Sidebar({ items = [], sections = [], footer, className }) {
  return (
    <nav className={cn("flex flex-col gap-5 rounded-2xl border border-line bg-paper-soft p-3", className)}>
      {items.length > 0 && <div className="space-y-1">{items.map(renderItem)}</div>}
      {sections.map((section) => (
        <div key={section.title}>
          {section.title && (
            <p className="mb-1.5 px-3 text-[10px] font-medium uppercase tracking-widest text-muted">
              {section.title}
            </p>
          )}
          <div className="space-y-1">{section.items.map(renderItem)}</div>
        </div>
      ))}
      {footer && <div className="mt-auto">{footer}</div>}
    </nav>
  );
}