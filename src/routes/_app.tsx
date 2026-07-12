import { createFileRoute, Outlet } from "@tanstack/react-router";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export const Route = createFileRoute("/_app")({
  component: AppLayoutRoute,
});

function AppLayoutRoute() {
  return (
    <DashboardLayout>
      <Outlet />
    </DashboardLayout>
  );
}
