import { useRouterState, Link } from "@tanstack/react-router";
import {
  Bell,
  ChevronRight,
  Menu,
  Moon,
  PanelLeft,
  Search,
  Sun,
} from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { navSections } from "./AppSidebar";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";

interface TopbarProps {
  onToggleDesktopSidebar: () => void;
  onOpenMobileNav: () => void;
}

function useBreadcrumbs() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const segments = pathname.split("/").filter(Boolean);
  const crumbs = segments.map((seg, i) => {
    const to = "/" + segments.slice(0, i + 1).join("/");
    const flat = navSections.flatMap((s) => s.items).find((it) => it.to === to);
    const label = flat?.label ?? seg.charAt(0).toUpperCase() + seg.slice(1);
    return { to, label };
  });
  return crumbs;
}

export function Topbar({ onToggleDesktopSidebar, onOpenMobileNav }: TopbarProps) {
  const crumbs = useBreadcrumbs();
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const isDark = theme === "dark";
  const userName = user?.full_name ?? "TransitOps User";
  const userRole = user?.role ?? "Team Member";
  const initials = getInitials(userName);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-card/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-card/80 sm:px-6">
      {/* Mobile: open drawer */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onOpenMobileNav}
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5" />
      </Button>

      {/* Desktop: collapse toggle */}
      <Button
        variant="ghost"
        size="icon"
        className="hidden lg:inline-flex"
        onClick={onToggleDesktopSidebar}
        aria-label="Toggle sidebar"
      >
        <PanelLeft className="h-5 w-5" />
      </Button>

      {/* Breadcrumbs */}
      <nav
        aria-label="Breadcrumb"
        className="hidden min-w-0 items-center gap-1.5 text-sm text-muted-foreground md:flex"
      >
        <Link to="/dashboard" className="hover:text-foreground">
          TransitOps
        </Link>
        {crumbs.map((c, idx) => (
          <span key={c.to} className="flex items-center gap-1.5">
            <ChevronRight className="h-3.5 w-3.5 shrink-0" />
            <span
              className={cn(
                "truncate",
                idx === crumbs.length - 1 ? "font-medium text-foreground" : "",
              )}
            >
              {c.label}
            </span>
          </span>
        ))}
      </nav>

      <div className="ml-auto flex items-center gap-2">
        {/* Search placeholder */}
        <div className="relative hidden md:block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search fleet, drivers, trips…"
            className="h-9 w-64 pl-9"
          />
        </div>

        <Button
          variant="ghost"
          size="icon"
          aria-label="Toggle theme"
          onClick={() => setTheme(isDark ? "light" : "dark")}
        >
          {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>

        <Button variant="ghost" size="icon" aria-label="Notifications" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-brand ring-2 ring-card" />
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className="flex items-center gap-2 rounded-full p-0.5 pr-2 outline-none transition-colors hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring"
              aria-label="User menu"
            >
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <span className="hidden text-left text-xs sm:block">
                <span className="block font-medium text-foreground leading-tight">{userName}</span>
                <span className="block text-muted-foreground leading-tight">{userRole}</span>
              </span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-52">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Preferences</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onSelect={() => logout()}>
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}

function getInitials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}
