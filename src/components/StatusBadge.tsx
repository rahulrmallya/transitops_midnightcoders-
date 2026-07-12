import { cn } from "@/lib/utils";

export type BadgeTone =
  | "success"
  | "info"
  | "warning"
  | "destructive"
  | "slate"
  | "brand"
  | "analytics"
  | "cyan";

const styles: Record<BadgeTone, string> = {
  success: "bg-success/12 text-success ring-success/20",
  info: "bg-info/12 text-info ring-info/20",
  warning: "bg-warning/20 text-warning ring-warning/25",
  destructive: "bg-destructive/12 text-destructive ring-destructive/20",
  slate: "bg-slate-muted/15 text-slate-muted ring-slate-muted/20 dark:text-muted-foreground",
  brand: "bg-brand/12 text-brand ring-brand/20",
  analytics: "bg-analytics/12 text-analytics ring-analytics/20",
  cyan: "bg-cyan-accent/20 text-cyan-accent ring-cyan-accent/25",
};

interface StatusBadgeProps {
  tone?: BadgeTone;
  children: React.ReactNode;
  dot?: boolean;
  className?: string;
}

export function StatusBadge({ tone = "info", children, dot = true, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
        styles[tone],
        className,
      )}
    >
      {dot ? (
        <span
          className={cn("h-1.5 w-1.5 rounded-full", {
            "bg-success": tone === "success",
            "bg-info": tone === "info",
            "bg-warning": tone === "warning",
            "bg-destructive": tone === "destructive",
            "bg-slate-muted": tone === "slate",
            "bg-brand": tone === "brand",
            "bg-analytics": tone === "analytics",
            "bg-cyan-accent": tone === "cyan",
          })}
        />
      ) : null}
      {children}
    </span>
  );
}
