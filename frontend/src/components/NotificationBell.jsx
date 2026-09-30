import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bell, CheckCheck } from "lucide-react";
import { api, apiPost } from "../api";

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [items, setItems] = useState([]);
  const boxRef = useRef(null);
  const navigate = useNavigate();

  const load = () => {
    api("/notifications/")
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || [];
        setItems(list.slice(0, 6));
        setUnread(list.filter((n) => !n.is_read).length);
      })
      .catch(() => {});
  };

  useEffect(() => {
    load();
    const timer = setInterval(load, 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    function onClickOutside(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  async function markAll() {
    await apiPost("/notifications/mark_all_read/").catch(() => {});
    setUnread(0);
    setItems((list) => list.map((n) => ({ ...n, is_read: true })));
  }

  function openItem(notification) {
    setOpen(false);
    if (notification.link) navigate(notification.link);
  }

  return (
    <div ref={boxRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="relative rounded-xl !p-2 transition active:scale-90"
        aria-label="Notifications"
        title="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unread > 0 && (
          <span className="animate-scale-in absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-glow px-1 text-[9px] font-bold text-white shadow-md">
            {unread}
          </span>
        )}
      </button>

      {open && (
        <div className="animate-scale-in absolute right-0 mt-2 w-80 max-w-[85vw] overflow-hidden rounded-2xl border border-line bg-paper shadow-xl">
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <p className="text-sm font-semibold">Notifications</p>
            {unread > 0 && (
              <button
                type="button"
                onClick={markAll}
                className="flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-brand hover:bg-brand/10"
              >
                <CheckCheck className="h-3.5 w-3.5" />
                Tout marquer lu
              </button>
            )}
          </div>
          <div className="max-h-80 overflow-y-auto">
            {items.length === 0 ? (
              <p className="px-4 py-6 text-center text-sm text-muted">Aucune notification.</p>
            ) : (
              items.map((n) => (
                <button
                  key={n.id}
                  type="button"
                  onClick={() => openItem(n)}
                  className={`flex w-full flex-col gap-0.5 border-b border-line/60 px-4 py-3 text-left transition hover:bg-ivory-soft ${
                    n.is_read ? "opacity-70" : ""
                  }`}
                >
                  <span className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium">{n.title}</span>
                    {!n.is_read && <span className="h-2 w-2 shrink-0 rounded-full bg-glow" />}
                  </span>
                  {n.message && <span className="text-xs text-muted">{n.message}</span>}
                </button>
              ))
            )}
          </div>
          <Link
            to="/student"
            className="block border-t border-line px-4 py-2.5 text-center text-xs text-muted hover:text-brand"
            onClick={() => setOpen(false)}
          >
            Voir mon espace
          </Link>
        </div>
      )}
    </div>
  );
}