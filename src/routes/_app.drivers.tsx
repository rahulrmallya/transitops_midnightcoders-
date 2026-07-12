import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  Users,
  CheckCircle2,
  Route as RouteIcon,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Eye,
  Mail,
  Phone,
} from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { StatsCard } from "@/components/StatsCard";
import { SearchBar } from "@/components/SearchBar";
import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { StatusBadge, type BadgeTone } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { drivers } from "@/store/sample-data";
import type { Driver, DriverStatus, LicenceStatus, SafetyBand } from "@/types";

export const Route = createFileRoute("/_app/drivers")({
  head: () => ({
    meta: [
      { title: "Drivers — TransitOps" },
      { name: "description", content: "Manage driver roster, licence compliance and safety." },
    ],
  }),
  component: DriversPage,
});

const statusTone: Record<DriverStatus, BadgeTone> = {
  Available: "success",
  "On Trip": "info",
  "Off Duty": "slate",
  Suspended: "destructive",
};

const licenceTone: Record<LicenceStatus, BadgeTone> = {
  Valid: "success",
  "Expiring Soon": "warning",
  Expired: "destructive",
};

const safetyTone: Record<SafetyBand, BadgeTone> = {
  High: "success",
  Medium: "warning",
  Low: "destructive",
};

const PAGE_SIZE = 6;

function initials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

function DriversPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [licenceFilter, setLicenceFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<Driver | null>(null);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return drivers.filter((d) => {
      const matchQ =
        !q ||
        d.name.toLowerCase().includes(q) ||
        d.licenceNumber.toLowerCase().includes(q) ||
        d.phone.toLowerCase().includes(q);
      const matchStatus = statusFilter === "all" || d.status === statusFilter;
      const matchLic = licenceFilter === "all" || d.licenceStatus === licenceFilter;
      return matchQ && matchStatus && matchLic;
    });
  }, [search, statusFilter, licenceFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const pageRows = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  const summary = useMemo(
    () => ({
      total: drivers.length,
      available: drivers.filter((d) => d.status === "Available").length,
      onTrip: drivers.filter((d) => d.status === "On Trip").length,
      attention: drivers.filter(
        (d) => d.licenceStatus !== "Valid" || d.status === "Suspended" || d.safetyBand === "Low",
      ).length,
    }),
    [],
  );

  const columns: DataTableColumn<Driver>[] = [
    {
      key: "driver",
      header: "Driver",
      render: (d) => (
        <div className="flex items-center gap-3">
          <Avatar className="h-9 w-9 shrink-0">
            <AvatarFallback className="bg-primary text-primary-foreground text-xs">
              {initials(d.name)}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-foreground">{d.name}</p>
            <p className="truncate text-xs text-muted-foreground">{d.phone}</p>
          </div>
        </div>
      ),
    },
    {
      key: "licence",
      header: "Licence No.",
      render: (d) => <span className="font-mono text-xs">{d.licenceNumber}</span>,
    },
    { key: "category", header: "Category", render: (d) => <span className="text-sm">{d.category}</span> },
    {
      key: "expiry",
      header: "Licence Expiry",
      render: (d) => (
        <div className="flex flex-col">
          <span className="text-sm tabular-nums">{d.licenceExpiry}</span>
          <StatusBadge tone={licenceTone[d.licenceStatus]} dot={false} className="mt-1 w-fit">
            {d.licenceStatus}
          </StatusBadge>
        </div>
      ),
    },
    {
      key: "safety",
      header: "Safety Score",
      render: (d) => (
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold tabular-nums">{d.safetyScore}</span>
          <StatusBadge tone={safetyTone[d.safetyBand]} dot={false}>
            {d.safetyBand}
          </StatusBadge>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (d) => <StatusBadge tone={statusTone[d.status]}>{d.status}</StatusBadge>,
    },
    {
      key: "actions",
      header: "Actions",
      headClassName: "text-right",
      className: "text-right",
      render: (d) => (
        <Button
          size="sm"
          variant="ghost"
          className="text-brand hover:text-brand"
          onClick={(e) => {
            e.stopPropagation();
            setSelected(d);
          }}
        >
          <Eye className="mr-1.5 h-3.5 w-3.5" /> View
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Drivers"
        description="Roster, licence compliance and safety at a glance."
        actions={
          <Button size="sm" className="bg-brand text-brand-foreground hover:bg-brand/90">
            Add driver
          </Button>
        }
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatsCard label="Total Drivers" value={summary.total} icon={Users} tone="info" />
        <StatsCard label="Available" value={summary.available} icon={CheckCircle2} tone="success" />
        <StatsCard label="On Trip" value={summary.onTrip} icon={RouteIcon} tone="brand" />
        <StatsCard label="Attention Required" value={summary.attention} icon={AlertTriangle} tone="warning" />
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
        <SearchBar
          value={search}
          onChange={(v) => {
            setSearch(v);
            setPage(1);
          }}
          placeholder="Search by name, phone or licence no."
        />
        <div className="flex flex-wrap items-center gap-2">
          <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
            <SelectTrigger className="h-10 w-[160px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              <SelectItem value="Available">Available</SelectItem>
              <SelectItem value="On Trip">On Trip</SelectItem>
              <SelectItem value="Off Duty">Off Duty</SelectItem>
              <SelectItem value="Suspended">Suspended</SelectItem>
            </SelectContent>
          </Select>
          <Select value={licenceFilter} onValueChange={(v) => { setLicenceFilter(v); setPage(1); }}>
            <SelectTrigger className="h-10 w-[170px]">
              <SelectValue placeholder="Licence status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All licences</SelectItem>
              <SelectItem value="Valid">Valid</SelectItem>
              <SelectItem value="Expiring Soon">Expiring Soon</SelectItem>
              <SelectItem value="Expired">Expired</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <DataTable
        columns={columns}
        rows={pageRows}
        rowKey={(d) => d.id}
        onRowClick={(d) => setSelected(d)}
        emptyTitle="No drivers match your filters"
        emptyDescription="Try clearing search or switching filters."
      />

      <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
        <p className="text-xs text-muted-foreground">
          Page <span className="font-medium text-foreground">{currentPage}</span> of{" "}
          <span className="font-medium text-foreground">{totalPages}</span> · {filtered.length}{" "}
          result{filtered.length === 1 ? "" : "s"}
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(Math.max(1, currentPage - 1))}
            disabled={currentPage <= 1}
          >
            <ChevronLeft className="h-4 w-4" /> Prev
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage >= totalPages}
          >
            Next <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <DriverDrawer driver={selected} onClose={() => setSelected(null)} />
    </div>
  );
}

function DriverDrawer({ driver, onClose }: { driver: Driver | null; onClose: () => void }) {
  return (
    <Sheet open={!!driver} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full sm:max-w-md overflow-y-auto">
        {driver && (
          <>
            <SheetHeader>
              <div className="flex items-center gap-3">
                <Avatar className="h-12 w-12">
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    {initials(driver.name)}
                  </AvatarFallback>
                </Avatar>
                <div className="min-w-0">
                  <SheetTitle className="truncate">{driver.name}</SheetTitle>
                  <SheetDescription>{driver.id}</SheetDescription>
                </div>
              </div>
            </SheetHeader>
            <div className="px-4 pb-6">
              <div className="mt-4 flex items-center justify-between rounded-lg border border-border bg-muted/40 px-3 py-2.5">
                <span className="text-xs text-muted-foreground">Current status</span>
                <StatusBadge tone={statusTone[driver.status]}>{driver.status}</StatusBadge>
              </div>

              <div className="mt-4 space-y-2 rounded-lg border border-border p-3 text-sm">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Phone className="h-3.5 w-3.5" />
                  <span className="text-foreground">{driver.phone}</span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Mail className="h-3.5 w-3.5" />
                  <span className="text-foreground truncate">{driver.email}</span>
                </div>
              </div>

              <Separator className="my-5" />

              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Licence
              </p>
              <dl className="space-y-3 text-sm">
                <Row label="Licence number" value={<span className="font-mono text-xs">{driver.licenceNumber}</span>} />
                <Row label="Category" value={driver.category} />
                <Row label="Expiry" value={driver.licenceExpiry} />
                <Row
                  label="Licence status"
                  value={<StatusBadge tone={licenceTone[driver.licenceStatus]}>{driver.licenceStatus}</StatusBadge>}
                />
              </dl>

              <Separator className="my-5" />

              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Safety & operations
              </p>
              <dl className="space-y-3 text-sm">
                <Row
                  label="Safety score"
                  value={
                    <span className="flex items-center gap-2">
                      <span className="font-semibold tabular-nums">{driver.safetyScore}</span>
                      <StatusBadge tone={safetyTone[driver.safetyBand]} dot={false}>
                        {driver.safetyBand}
                      </StatusBadge>
                    </span>
                  }
                />
                <Row label="Trips (30d)" value="—" />
                <Row label="Kilometers (30d)" value="—" />
                <Row label="Incidents" value="—" />
              </dl>
              <p className="mt-3 text-xs text-muted-foreground">
                Operational summary will populate once trip data is connected.
              </p>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-medium text-foreground">{value}</dd>
    </div>
  );
}
