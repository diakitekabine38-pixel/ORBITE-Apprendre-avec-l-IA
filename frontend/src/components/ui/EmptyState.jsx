import { Inbox } from "lucide-react";
import { cn } from "./cn";

export default function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-3xl border border-dashed border-line bg-paper-soft p-10 text-center",
        className,
      )}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-orbital-100 text-orbital-600">
        <Icon className="h-6 w-6" />
      </div>
      {title && <h3 className="font-display text-lg font-semibold text-ink-deep">{title}</h3>}
      {description && <p className="max-w-sm text-sm text-ink-soft">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}