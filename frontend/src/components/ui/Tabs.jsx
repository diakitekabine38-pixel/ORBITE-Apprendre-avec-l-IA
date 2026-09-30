import { useState } from "react";
import { cn } from "./cn";

export default function Tabs({ items, value, defaultValue, onChange, className }) {
  const [internal, setInternal] = useState(defaultValue ?? items[0]?.value);
  const active = value ?? internal;
  const activeItem = items.find((i) => i.value === active);

  const select = (v) => {
    if (value === undefined) setInternal(v);
    onChange?.(v);
  };

  return (
    <div>
      <div
        role="tablist"
        className={cn("flex w-fit gap-1 rounded-2xl bg-ivory-soft p-1", className)}
      >
        {items.map((item) => {
          const isActive = item.value === active;
          return (
            <button
              key={item.value}
              type="button"
              role="tab"
              aria-selected={isActive}
              onClick={() => select(item.value)}
              className={cn(
                "inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm transition-all",
                isActive
                  ? "bg-paper font-medium text-ink-deep shadow-card"
                  : "text-ink-soft hover:text-ink-deep",
              )}
            >
              {item.icon && <item.icon className="h-4 w-4" />}
              {item.label}
            </button>
          );
        })}
      </div>
      {activeItem?.content && <div className="mt-4">{activeItem.content}</div>}
    </div>
  );
}