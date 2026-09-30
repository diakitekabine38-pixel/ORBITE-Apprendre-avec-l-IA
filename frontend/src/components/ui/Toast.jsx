import { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { AlertTriangle, CheckCircle2, Info, X, XCircle } from "lucide-react";
import { cn } from "./cn";

const ToastContext = createContext(null);

const ICONS = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

const COLORS = {
  success: "bg-success-soft text-success",
  error: "bg-error-soft text-error",
  warning: "bg-warning-soft text-warning",
  info: "bg-info-soft text-info",
};

const BORDERS = {
  success: "border-success/25",
  error: "border-error/25",
  warning: "border-warning/25",
  info: "border-info/25",
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const dismiss = useCallback((id) => {
    setToasts((list) => list.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(
    ({ type = "info", title, description, icon: CustomIcon, duration = 4500 } = {}) => {
      const id = ++idRef.current;
      setToasts((list) => [...list, { id, type, title, description, icon: CustomIcon }]);
      if (duration > 0) {
        setTimeout(() => dismiss(id), duration);
      }
    },
    [dismiss],
  );

  const value = useMemo(() => ({ toast }), [toast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      {createPortal(
        <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2">
          {toasts.map((t) => {
            const Icon = t.icon || ICONS[t.type] || Info;
            return (
              <div
                key={t.id}
                role="status"
                className={cn(
                  "animate-toast-in pointer-events-auto flex items-start gap-3 rounded-2xl border bg-paper p-4 shadow-elevated",
                  BORDERS[t.type],
                )}
              >
                <div className={cn("flex h-8 w-8 shrink-0 items-center justify-center rounded-full", COLORS[t.type])}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  {t.title && <p className="text-sm font-medium text-ink-deep">{t.title}</p>}
                  {t.description && <p className="mt-0.5 text-xs text-ink-soft">{t.description}</p>}
                </div>
                <button
                  type="button"
                  onClick={() => dismiss(t.id)}
                  className="shrink-0 text-muted transition-colors hover:text-ink-deep"
                  aria-label="Fermer"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            );
          })}
        </div>,
        document.body,
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast doit être utilisé dans un <ToastProvider>");
  return ctx;
}

export default ToastProvider;