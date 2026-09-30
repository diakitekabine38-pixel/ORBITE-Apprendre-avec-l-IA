import { cn } from "./cn";

export function Table({ className, children, ...props }) {
  return (
    <div className={cn("w-full overflow-x-auto rounded-2xl border border-line bg-paper", className)}>
      <table className="w-full text-left text-sm" {...props}>
        {children}
      </table>
    </div>
  );
}

export function TableHead({ className, children, ...props }) {
  return (
    <thead className={cn("border-b border-line", className)} {...props}>
      {children}
    </thead>
  );
}

export function TableRow({ className, children, ...props }) {
  return (
    <tr className={cn("transition-colors hover:bg-paper-soft", className)} {...props}>
      {children}
    </tr>
  );
}

export function TableHeadCell({ className, children, ...props }) {
  return (
    <th className={cn("px-3 py-3 font-medium text-ink-soft", className)} {...props}>
      {children}
    </th>
  );
}

export function TableCell({ className, children, ...props }) {
  return (
    <td className={cn("border-b border-line-soft px-3 py-3 text-ink-deep", className)} {...props}>
      {children}
    </td>
  );
}

export default Table;