import { useId, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "./cn";

export default function Input({
  label,
  error,
  hint,
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  type = "text",
  className,
  id,
  ...props
}) {
  const autoId = useId();
  const inputId = id || autoId;
  const [show, setShow] = useState(false);
  const isPassword = type === "password";

  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-ink-soft">
          {label}
        </label>
      )}
      <div className="relative">
        {LeftIcon && (
          <LeftIcon className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
        )}
        <input
          id={inputId}
          type={isPassword && show ? "text" : type}
          aria-invalid={!!error}
          className={cn(
            "w-full rounded-2xl border border-line bg-paper px-4 py-3 text-sm text-ink-deep outline-none transition-all placeholder:text-ink-faint focus:border-orbital-400 focus:ring-2 focus:ring-orbital-400/25 disabled:opacity-50",
            LeftIcon && "pl-11",
            (RightIcon || isPassword) && "pr-12",
            error && "border-error focus:border-error focus:ring-error/25",
            className,
          )}
          {...props}
        />
        {isPassword ? (
          <button
            type="button"
            onClick={() => setShow((v) => !v)}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-muted transition-colors hover:text-orbital-600"
            aria-label={show ? "Masquer le mot de passe" : "Afficher le mot de passe"}
          >
            {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        ) : RightIcon ? (
          <RightIcon className="absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
        ) : null}
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