import { cn } from "./cn";

const GRADIENTS = {
  orbital: "bg-orbital-gradient",
  kodex: "bg-gradient-to-br from-kodex-light to-kodex",
  kora: "bg-gradient-to-br from-kora-light to-kora",
  nova: "bg-gradient-to-br from-nova-light to-nova",
  pixel: "bg-gradient-to-br from-pixel-light to-pixel",
};

const TEXT = {
  orbital: "text-white",
  kodex: "text-white",
  kora: "text-white",
  nova: "text-ink",
  pixel: "text-white",
};

const SIZES = {
  xs: "h-6 w-6 text-[10px]",
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-16 w-16 text-xl",
  xl: "h-24 w-24 text-3xl",
};

function initials(name = "") {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase())
    .join("");
}

export default function Avatar({
  name,
  src,
  size = "md",
  gradient = "orbital",
  className,
}) {
  const base = cn(
    "flex shrink-0 items-center justify-center rounded-full font-display font-700",
    GRADIENTS[gradient] || GRADIENTS.orbital,
    TEXT[gradient] || TEXT.orbital,
    SIZES[size],
    className,
  );

  if (src) {
    return <img src={src} alt={name || "Avatar"} className={cn(base, "object-cover")} />;
  }

  return (
    <span className={base} aria-label={name}>
      {initials(name) || "?"}
    </span>
  );
}