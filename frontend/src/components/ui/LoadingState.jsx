import { Loader2 } from "lucide-react";
import { cn } from "./cn";

const SPIN = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-8 w-8",
};

export default function LoadingState({ label = "Chargement…", size = "md", full = false, className }) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 py-12 text-muted",
        full && "min-h-60",
        className,
      )}
    >
      <Loader2 className={cn("animate-spin text-orbital-500", SPIN[size])} />
      {label && <p className="text-sm">{label}</p>}
    </div>
  );
}