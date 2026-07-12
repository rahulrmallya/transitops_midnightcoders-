import { createFileRoute } from "@tanstack/react-router";
import { BarChart3 } from "lucide-react";
import { PlaceholderPage } from "@/components/PlaceholderPage";

export const Route = createFileRoute("/_app/reports")({
  head: () => ({ meta: [{ title: "Reports — TransitOps" }] }),
  component: () => (
    <PlaceholderPage
      title="Reports"
      description="Actionable insights across utilization, cost and compliance."
      icon={BarChart3}
    />
  ),
});
