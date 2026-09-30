import { Link } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { cn } from "./cn";

const VARIANTS = {
  primary: "bg-orbital-600 text-white hover:bg-orbital-700 hover:shadow-card-hover",
  gradient: "bg-orbital-gradient text-white hover:shadow-[0_0_30px_rgba(139,92,246,0.25)]",
  secondary:
    "border border-line bg-paper text-ink-deep hover:border-orbital-400 hover:bg-paper-soft",
  tone: "bg-ivory-soft text-ink-deep hover:bg-ivory-warm",
  outline: "border border-orbital-400 text-orbital-600 hover:bg-orbital-50",
  ghost: "text-ink-soft hover:text-orbital-600",
  danger: "bg-error text-white hover:brightness-110",
};

const SIZES = {
  sm: "px-4 py-1.5 text-xs",
  md: "px-5 py-2.5 text-sm",
  lg: "px-7 py-3.5 text-base",
};

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  icon: Icon,
  to,
  className,
  children,
  disabled,
  type = "button",
  ...props
}) {
  const classes = cn(
    "inline-flex items-center justify-center gap-2 rounded-full font-medium transition-all active:scale-95 disabled:pointer-events-none disabled:opacity-40",
    VARIANTS[variant],
    SIZES[size],
    className,
  );

  const inner = (
    <>
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : Icon ? (
        <Icon className="h-4 w-4" />
      ) : null}
      {children}
    </>
  );

  if (to) {
    return (
      <Link to={to} className={classes} {...props}>
        {inner}
      </Link>
    );
  }

  return (
    <button type={type} className={classes} disabled={disabled || loading} {...props}>
      {inner}
    </button>
  );
}