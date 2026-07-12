import { createFileRoute } from "@tanstack/react-router";
import { Wrench } from "lucide-react";
import { PlaceholderPage } from "@/components/PlaceholderPage";

export const Route = createFileRoute("/_app/maintenance")({
  head: () => ({ meta: [{ title: "Maintenance — TransitOps" }] }),
  component: () => (
    <PlaceholderPage
      title="Maintenance"
      description="Schedule service, track work orders and reduce downtime."
      icon={Wrench}
    />
  ),
});
