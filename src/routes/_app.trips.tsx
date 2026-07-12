import { createFileRoute } from "@tanstack/react-router";
import { Route as RouteIcon } from "lucide-react";
import { PlaceholderPage } from "@/components/PlaceholderPage";

export const Route = createFileRoute("/_app/trips")({
  head: () => ({ meta: [{ title: "Trips — TransitOps" }] }),
  component: () => (
    <PlaceholderPage
      title="Trips"
      description="Plan, dispatch and monitor trips across your fleet."
      icon={RouteIcon}
    />
  ),
});
