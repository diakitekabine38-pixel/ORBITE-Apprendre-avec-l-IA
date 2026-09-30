import { AlertTriangle } from "lucide-react";
import Button from "./Button";
import { cn } from "./cn";

export default function ErrorState({
  title = "Une erreur est survenue",
  message,
  onRetry,
  action,
  className,
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-3xl border border-error/25 bg-error-soft p-10 text-center",
        className,
      )}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-error/15 text-error">
        <AlertTriangle className="h-6 w-6" />
      </div>
      {title && <h3 className="font-display text-lg font-semibold text-ink-deep">{title}</h3>}
      {message && <p className="max-w-sm text-sm text-ink-soft">{message}</p>}
      {(onRetry || action) && (
        <div className="mt-2 flex items-center gap-3">
          {onRetry && (
            <Button variant="secondary" size="sm" onClick={onRetry}>
              Réessayer
            </Button>
          )}
          {action}
        </div>
      )}
    </div>
  );
}