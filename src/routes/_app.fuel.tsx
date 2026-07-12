import { createFileRoute } from "@tanstack/react-router";
import { Fuel } from "lucide-react";
import { PlaceholderPage } from "@/components/PlaceholderPage";

export const Route = createFileRoute("/_app/fuel")({
  head: () => ({ meta: [{ title: "Fuel — TransitOps" }] }),
  component: () => (
    <PlaceholderPage
      title="Fuel"
      description="Log refills, analyze consumption and control fuel spend."
      icon={Fuel}
    />
  ),
});
