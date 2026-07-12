import { createFileRoute } from "@tanstack/react-router";
import { Settings } from "lucide-react";
import { PlaceholderPage } from "@/components/PlaceholderPage";

export const Route = createFileRoute("/_app/settings")({
  head: () => ({ meta: [{ title: "Settings — TransitOps" }] }),
  component: () => (
    <PlaceholderPage
      title="Settings"
      description="Workspace preferences, roles and integrations."
      icon={Settings}
    />
  ),
});
