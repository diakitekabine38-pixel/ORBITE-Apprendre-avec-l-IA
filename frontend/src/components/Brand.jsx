import { Link } from "react-router-dom";

export default function Brand({ to = "/" }) {
  return (
    <Link to={to} className="group flex shrink-0 items-center gap-2 font-display">
      <span className="flex h-9 w-9 items-center justify-center rounded-2xl border border-line bg-paper p-1 shadow-sm transition-all duration-300 group-hover:border-brand/60 group-active:scale-95">
        <img src="/logo.svg" alt="ORBITE" className="h-6 w-6 object-contain" />
      </span>
      <span className="text-lg font-semibold tracking-tight">ORBITE</span>
    </Link>
  );
}