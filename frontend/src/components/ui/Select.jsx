import { useId } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "./cn";

export default function Select({ label, error, hint, className, id, children, ...props }) {
  const autoId = useId();
  const selectId = id || autoId;

  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={selectId} className="block text-sm font-medium text-ink-soft">
          {label}
        </label>
      )}
      <div className="relative">
        <select
          id={selectId}
          className={cn(
            "w-full appearance-none rounded-2xl border border-line bg-paper px-4 py-3 pr-10 text-sm text-ink-deep outline-none transition-all focus:border-orbital-400 focus:ring-2 focus:ring-orbital-400/25 disabled:opacity-50",
            error && "border-error focus:border-error focus:ring-error/25",
            className,
          )}
          {...props}
        >
          {children}
        </select>
        <ChevronDown className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
      </div>
      {error ? (
        <p className="text-xs text-error" role="alert">
          {error}
        </p>
      ) : hint ? (
        <p className="text-xs text-muted">{hint}</p>
      ) : null}
    </div>
  );
}