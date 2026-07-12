import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SectionTitleProps {
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function SectionTitle({ title, description, action, className }: SectionTitleProps) {
  return (
    <div className={cn("flex items-center justify-between gap-3", className)}>
      <div className="min-w-0">
        <h2 className="text-base font-semibold text-foreground">{title}</h2>
        {description ? (
          <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {action}
    </div>
  );
}
