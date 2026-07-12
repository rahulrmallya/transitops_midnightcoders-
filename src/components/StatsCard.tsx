import type { LucideIcon } from "lucide-react";
import { TrendingDown, TrendingUp } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type Tone = "brand" | "info" | "success" | "warning" | "analytics" | "cyan" | "destructive";

const toneStyles: Record<Tone, { bg: string; fg: string }> = {
  brand: { bg: "bg-brand/10", fg: "text-brand" },
  info: { bg: "bg-info/10", fg: "text-info" },
  success: { bg: "bg-success/10", fg: "text-success" },
  warning: { bg: "bg-warning/15", fg: "text-warning" },
  analytics: { bg: "bg-analytics/10", fg: "text-analytics" },
  cyan: { bg: "bg-cyan-accent/15", fg: "text-cyan-accent" },
  destructive: { bg: "bg-destructive/10", fg: "text-destructive" },
};

interface StatsCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: Tone;
  delta?: { value: string; direction: "up" | "down" };
  hint?: string;
}

export function StatsCard({ label, value, icon: Icon, tone = "info", delta, hint }: StatsCardProps) {
  const t = toneStyles[tone];
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {label}
            </p>
            <p className="mt-2 text-3xl font-semibold tracking-tight text-foreground">
              {value}
            </p>
            {hint ? (
              <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
            ) : null}
          </div>
          <div className={cn("grid h-11 w-11 shrink-0 place-items-center rounded-xl", t.bg)}>
            <Icon className={cn("h-5 w-5", t.fg)} />
          </div>
        </div>
        {delta ? (
          <div className="mt-4 flex items-center gap-1.5 text-xs">
            <span
              className={cn(
                "inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-medium",
                delta.direction === "up"
                  ? "bg-success/10 text-success"
                  : "bg-destructive/10 text-destructive",
              )}
            >
              {delta.direction === "up" ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              {delta.value}
            </span>
            <span className="text-muted-foreground">vs last week</span>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
