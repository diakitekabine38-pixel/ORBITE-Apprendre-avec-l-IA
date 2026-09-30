import { NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../auth";
import { mobileItemsFor } from "../navigation";

export default function MobileTabBar() {
  const { user } = useAuth();
  const location = useLocation();

  const items = mobileItemsFor(user);

  return (
    <nav
      aria-label="Navigation principale mobile"
      className="fixed inset-x-0 bottom-0 z-50 border-t border-line bg-paper/95 backdrop-blur-xl lg:hidden"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <div className="mx-auto flex max-w-lg items-stretch justify-around px-2 py-1.5">
        {items.map((item) => {
          const isActive = item.to === "/"
            ? location.pathname === item.to
            : location.pathname.startsWith(item.to);
          return (
            <NavLink
              key={item.key}
              to={item.to}
              className={`relative flex flex-1 flex-col items-center justify-center gap-0.5 rounded-2xl px-1 py-1.5 transition-all duration-200 active:scale-90 ${
                isActive ? "font-semibold text-brand" : "text-muted hover:text-ink-deep"
              }`}
            >
              <span className="relative">
                <item.icon className="h-5 w-5" />
              </span>
              <span className="max-w-full truncate text-[10px] tracking-tight">{item.label}</span>
              {isActive && <span className="absolute -bottom-1 h-0.5 w-5 rounded-full bg-brand" />}
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}