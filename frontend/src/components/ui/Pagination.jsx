import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "./cn";

function pages(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const set = new Set([1, 2, total - 1, total, current - 1, current, current + 1]);
  const sorted = [...set].filter((p) => p >= 1 && p <= total).sort((a, b) => a - b);
  return sorted.reduce((acc, p, i, arr) => {
    if (i > 0 && p - arr[i - 1] > 1) acc.push("...");
    acc.push(p);
    return acc;
  }, []);
}

export default function Pagination({ page, total, onChange, className }) {
  if (total <= 1) return null;
  const list = pages(page, total);

  const navCls =
    "flex h-9 w-9 items-center justify-center rounded-full text-ink-soft transition-colors hover:bg-ivory-soft hover:text-ink-deep disabled:pointer-events-none disabled:opacity-40";

  return (
    <nav className={cn("flex items-center gap-1", className)} aria-label="Pagination">
      <button
        type="button"
        onClick={() => onChange?.(page - 1)}
        disabled={page <= 1}
        className={navCls}
        aria-label="Page précédente"
      >
        <ChevronLeft className="h-4 w-4" />
      </button>
      {list.map((p, i) =>
        p === "..." ? (
          <span key={`ellipsis-${i}`} className="px-1 text-sm text-muted">
            …
          </span>
        ) : (
          <button
            key={p}
            type="button"
            onClick={() => onChange?.(p)}
            aria-current={p === page ? "page" : undefined}
            className={cn(
              "h-9 w-9 rounded-full text-sm font-medium transition-colors",
              p === page
                ? "bg-orbital-600 text-white"
                : "text-ink-soft hover:bg-ivory-soft hover:text-ink-deep",
            )}
          >
            {p}
          </button>
        ),
      )}
      <button
        type="button"
        onClick={() => onChange?.(page + 1)}
        disabled={page >= total}
        className={navCls}
        aria-label="Page suivante"
      >
        <ChevronRight className="h-4 w-4" />
      </button>
    </nav>
  );
}