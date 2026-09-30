import { cn } from "./cn";

const VARIANTS = {
  neutral: "bg-paper-soft text-ink-soft border border-line",
  brand: "bg-orbital-100 text-orbital-700",
  success: "bg-success-soft text-success",
  warning: "bg-warning-soft text-warning",
  error: "bg-error-soft text-error",
  info: "bg-info-soft text-info",
  kodex: "bg-kodex-soft text-kodex",
  kora: "bg-kora-soft text-kora",
  nova: "bg-nova-soft text-nova-dark",
  pixel: "bg-pixel-soft text-pixel",
  gradient: "bg-orbital-gradient text-white",
};

const DOTS = {
  neutral: "bg-ink-soft",
  brand: "bg-orbital-600",
  success: "bg-success",
  warning: "bg-warning",
  error: "bg-error",
  info: "bg-info",
  kodex: "bg-kodex",
  kora: "bg-kora",
  nova: "bg-nova",
  pixel: "bg-pixel",
  gradient: "bg-white",
};

export default function Badge({
  variant = "neutral",
  dot = false,
  icon: Icon,
  className,
  children,
  ...props
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium",
        VARIANTS[variant],
        className,
      )}
      {...props}
    >
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full", DOTS[variant])} />}
      {Icon && <Icon className="h-3 w-3" />}
      {children}
    </span>
  );
}