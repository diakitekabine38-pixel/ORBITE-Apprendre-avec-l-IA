import { cn } from "./cn";

const STYLES = {
  default: "bg-paper border border-line shadow-card",
  elevated: "bg-paper border border-line shadow-elevated",
  interactive:
    "bg-paper border border-line shadow-card transition-all duration-300 hover:-translate-y-1 hover:shadow-card-hover",
  dark: "border border-line bg-ink-deep text-paper shadow-card",
};

export default function Card({
  variant = "default",
  padding = true,
  className,
  children,
  ...props
}) {
  return (
    <div className={cn(STYLES[variant], "rounded-3xl", padding && "p-6", className)} {...props}>
      {children}
    </div>
  );
}