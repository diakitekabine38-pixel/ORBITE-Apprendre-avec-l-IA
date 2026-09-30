import { useId } from "react";
import { cn } from "./cn";

export default function Textarea({ label, error, hint, className, id, ...props }) {
  const autoId = useId();
  const textareaId = id || autoId;

  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={textareaId} className="block text-sm font-medium text-ink-soft">
          {label}
        </label>
      )}
      <textarea
        id={textareaId}
        className={cn(
          "w-full resize-none rounded-2xl border border-line bg-paper px-4 py-3 text-sm text-ink-deep outline-none transition-all placeholder:text-ink-faint focus:border-orbital-400 focus:ring-2 focus:ring-orbital-400/25 disabled:opacity-50",
          error && "border-error focus:border-error focus:ring-error/25",
          className,
        )}
        {...props}
      />
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