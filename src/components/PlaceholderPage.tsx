import type { LucideIcon } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface PlaceholderPageProps {
  title: string;
  description: string;
  icon: LucideIcon;
  note?: string;
}

export function PlaceholderPage({ title, description, icon: Icon, note }: PlaceholderPageProps) {
  return (
    <div className="space-y-6">
      <PageHeader title={title} description={description} />

      <Card>
        <CardContent className="p-8">
          <div className="flex flex-col items-center gap-4 py-8 text-center">
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-brand/10 text-brand">
              <Icon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-base font-semibold text-foreground">{title} module</p>
              <p className="mt-1 max-w-md text-sm text-muted-foreground">
                {note ??
                  "This module will be available soon. The interface is being prepared for integration with the operations backend."}
              </p>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-xl border border-border p-4">
                <div className="flex items-center justify-between">
                  <Skeleton className="h-3 w-24" />
                  <Skeleton className="h-8 w-8 rounded-lg" />
                </div>
                <Skeleton className="mt-4 h-7 w-20" />
                <Skeleton className="mt-2 h-3 w-32" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
