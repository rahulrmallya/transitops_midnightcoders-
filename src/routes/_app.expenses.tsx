import { createFileRoute } from "@tanstack/react-router";
import { Wallet } from "lucide-react";
import { PlaceholderPage } from "@/components/PlaceholderPage";

export const Route = createFileRoute("/_app/expenses")({
  head: () => ({ meta: [{ title: "Expenses — TransitOps" }] }),
  component: () => (
    <PlaceholderPage
      title="Expenses"
      description="Consolidate operating costs across vehicles, drivers and trips."
      icon={Wallet}
    />
  ),
});
