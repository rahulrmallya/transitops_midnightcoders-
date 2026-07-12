import { Link, useRouterState } from "@tanstack/react-router";
import {
  LayoutDashboard,
  Truck,
  Users,
  Route as RouteIcon,
  Wrench,
  Fuel,
  Wallet,
  BarChart3,
  Settings,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  label: string;
  to: string;
  icon: typeof LayoutDashboard;
}

interface NavSection {
  label: string;
  items: NavItem[];
}

export const navSections: NavSection[] = [
  {
    label: "Overview",
    items: [{ label: "Dashboard", to: "/dashboard", icon: LayoutDashboard }],
  },
  {
    label: "Operations",
    items: [
      { label: "Vehicles", to: "/vehicles", icon: Truck },
      { label: "Drivers", to: "/drivers", icon: Users },
      { label: "Trips", to: "/trips", icon: RouteIcon },
    ],
  },
  {
    label: "Fleet Management",
    items: [
      { label: "Maintenance", to: "/maintenance", icon: Wrench },
      { label: "Fuel", to: "/fuel", icon: Fuel },
      { label: "Expenses", to: "/expenses", icon: Wallet },
    ],
  },
  {
    label: "Insights",
    items: [{ label: "Reports", to: "/reports", icon: BarChart3 }],
  },
  {
    label: "System",
    items: [{ label: "Settings", to: "/settings", icon: Settings }],
  },
];

interface AppSidebarProps {
  collapsed?: boolean;
  onNavigate?: () => void;
}

export function AppSidebar({ collapsed = false, onNavigate }: AppSidebarProps) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <aside
      className={cn(
        "flex h-full flex-col bg-sidebar text-sidebar-foreground",
        collapsed ? "w-[76px]" : "w-64",
      )}
    >
      {/* Brand */}
      <div
        className={cn(
          "flex h-16 items-center gap-3 border-b border-sidebar-border px-4",
          collapsed && "justify-center px-2",
        )}
      >
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-brand text-brand-foreground shadow-sm">
          <Truck className="h-5 w-5" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-white">TransitOps</p>
            <p className="truncate text-[11px] text-sidebar-foreground/70">
              Transport Operations
            </p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="space-y-5">
          {navSections.map((section) => (
            <li key={section.label}>
              {!collapsed && (
                <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-sidebar-foreground/50">
                  {section.label}
                </p>
              )}
              <ul className="space-y-1">
                {section.items.map((item) => {
                  const active = pathname === item.to;
                  const Icon = item.icon;
                  return (
                    <li key={item.to}>
                      <Link
                        to={item.to}
                        onClick={onNavigate}
                        className={cn(
                          "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                          active
                            ? "bg-brand text-brand-foreground shadow-sm"
                            : "text-sidebar-foreground/85 hover:bg-sidebar-accent hover:text-white",
                          collapsed && "justify-center px-2",
                        )}
                      >
                        <Icon className={cn("h-[18px] w-[18px] shrink-0")} />
                        {!collapsed && <span className="truncate">{item.label}</span>}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </li>
          ))}
        </ul>
      </nav>

      {/* Logout */}
      <div className="border-t border-sidebar-border p-3">
        <Link
          to="/login"
          onClick={onNavigate}
          className={cn(
            "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-sidebar-foreground/80 transition-colors hover:bg-sidebar-accent hover:text-white",
            collapsed && "justify-center px-2",
          )}
        >
          <LogOut className="h-[18px] w-[18px]" />
          {!collapsed && <span>Logout</span>}
        </Link>
      </div>
    </aside>
  );
}
