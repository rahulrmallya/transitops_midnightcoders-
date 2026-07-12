import { createFileRoute, Outlet, redirect, useNavigate } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useEffect } from "react";
import { DashboardLayout } from "@/layouts/DashboardLayout";
import { useAuth } from "@/contexts/AuthContext";
import { getAccessToken } from "@/lib/auth-storage";

export const Route = createFileRoute("/_app")({
  beforeLoad: () => {
    if (typeof window !== "undefined" && !getAccessToken()) {
      throw redirect({ to: "/login" });
    }
  },
  component: AppLayoutRoute,
});

function AppLayoutRoute() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate({ to: "/login", replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  if (isLoading || !isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  return (
    <DashboardLayout>
      <Outlet />
    </DashboardLayout>
  );
}
