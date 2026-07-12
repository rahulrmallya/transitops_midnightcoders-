import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  Truck,
  CheckCircle2,
  Route as RouteIcon,
  Wrench,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  Eye,
} from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { StatsCard } from "@/components/StatsCard";
import { SearchBar } from "@/components/SearchBar";
import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { StatusBadge, type BadgeTone } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
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
import { vehicles } from "@/store/sample-data";
import type { Vehicle, VehicleStatus } from "@/types";

export const Route = createFileRoute("/_app/vehicles")({
  head: () => ({
    meta: [
      { title: "Vehicles — TransitOps" },
      { name: "description", content: "Manage and monitor your fleet vehicles." },
    ],
  }),
  component: VehiclesPage,
});

const statusTone: Record<VehicleStatus, BadgeTone> = {
  Available: "success",
  "On Trip": "info",
  "In Maintenance": "warning",
  Retired: "slate",
};

const PAGE_SIZE = 6;

function VehiclesPage() {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [sortKey, setSortKey] = useState<"name" | "odometer">("name");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<Vehicle | null>(null);

  const types = useMemo(
    () => Array.from(new Set(vehicles.map((v) => v.type))).sort(),
    [],
  );

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    let rows = vehicles.filter((v) => {
      const matchQ =
        !q ||
        v.name.toLowerCase().includes(q) ||
        v.registration.toLowerCase().includes(q) ||
        v.type.toLowerCase().includes(q);
      const matchType = typeFilter === "all" || v.type === typeFilter;
      const matchStatus = statusFilter === "all" || v.status === statusFilter;
      return matchQ && matchType && matchStatus;
    });
    rows = [...rows].sort((a, b) => {
      if (sortKey === "odometer") return b.odometer - a.odometer;
      return a.name.localeCompare(b.name);
    });
    return rows;
  }, [search, typeFilter, statusFilter, sortKey]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const pageRows = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  const summary = useMemo(() => {
    return {
      total: vehicles.length,
      available: vehicles.filter((v) => v.status === "Available").length,
      onTrip: vehicles.filter((v) => v.status === "On Trip").length,
      maintenance: vehicles.filter((v) => v.status === "In Maintenance").length,
    };
  }, []);

  const columns: DataTableColumn<Vehicle>[] = [
    {
      key: "vehicle",
      header: "Vehicle",
      render: (v) => (
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-info/10 text-info">
            <Truck className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-foreground">{v.name}</p>
            <p className="truncate text-xs text-muted-foreground">{v.id}</p>
          </div>
        </div>
      ),
    },
    {
      key: "registration",
      header: "Registration",
      render: (v) => <span className="font-mono text-sm">{v.registration}</span>,
    },
    { key: "type", header: "Type", render: (v) => <span className="text-sm">{v.type}</span> },
    {
      key: "capacity",
      header: "Capacity",
      render: (v) => <span className="text-sm text-muted-foreground">{v.capacity}</span>,
    },
    {
      key: "odometer",
      header: "Odometer",
      render: (v) => <span className="text-sm tabular-nums">{v.odometer.toLocaleString()} km</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (v) => <StatusBadge tone={statusTone[v.status]}>{v.status}</StatusBadge>,
    },
    {
      key: "actions",
      header: "Actions",
      headClassName: "text-right",
      className: "text-right",
      render: (v) => (
        <Button
          size="sm"
          variant="ghost"
          className="text-brand hover:text-brand"
          onClick={(e) => {
            e.stopPropagation();
            setSelected(v);
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
        title="Vehicles"
        description="Track availability, maintenance and utilization across your fleet."
        actions={
          <Button size="sm" className="bg-brand text-brand-foreground hover:bg-brand/90">
            Add vehicle
          </Button>
        }
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatsCard label="Total Vehicles" value={summary.total} icon={Truck} tone="info" />
        <StatsCard label="Available" value={summary.available} icon={CheckCircle2} tone="success" />
        <StatsCard label="On Trip" value={summary.onTrip} icon={RouteIcon} tone="brand" />
        <StatsCard label="In Maintenance" value={summary.maintenance} icon={Wrench} tone="warning" />
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
        <SearchBar
          value={search}
          onChange={(v) => {
            setSearch(v);
            setPage(1);
          }}
          placeholder="Search by name, reg no. or type"
        />
        <div className="flex flex-wrap items-center gap-2">
          <Select value={typeFilter} onValueChange={(v) => { setTypeFilter(v); setPage(1); }}>
            <SelectTrigger className="h-10 w-[160px]">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All types</SelectItem>
              {types.map((t) => (
                <SelectItem key={t} value={t}>{t}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
            <SelectTrigger className="h-10 w-[160px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              <SelectItem value="Available">Available</SelectItem>
              <SelectItem value="On Trip">On Trip</SelectItem>
              <SelectItem value="In Maintenance">In Maintenance</SelectItem>
              <SelectItem value="Retired">Retired</SelectItem>
            </SelectContent>
          </Select>
          <Select value={sortKey} onValueChange={(v: "name" | "odometer") => setSortKey(v)}>
            <SelectTrigger className="h-10 w-[170px]">
              <ArrowUpDown className="mr-1 h-3.5 w-3.5" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="name">Sort: Name</SelectItem>
              <SelectItem value="odometer">Sort: Odometer</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <DataTable
        columns={columns}
        rows={pageRows}
        rowKey={(v) => v.id}
        onRowClick={(v) => setSelected(v)}
        emptyTitle="No vehicles match your filters"
        emptyDescription="Try clearing search or switching filters."
      />

      <PaginationBar
        page={currentPage}
        totalPages={totalPages}
        total={filtered.length}
        onPage={setPage}
      />

      <VehicleDrawer vehicle={selected} onClose={() => setSelected(null)} />
    </div>
  );
}

function PaginationBar({
  page,
  totalPages,
  total,
  onPage,
}: {
  page: number;
  totalPages: number;
  total: number;
  onPage: (p: number) => void;
}) {
  return (
    <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
      <p className="text-xs text-muted-foreground">
        Page <span className="font-medium text-foreground">{page}</span> of{" "}
        <span className="font-medium text-foreground">{totalPages}</span> · {total} result
        {total === 1 ? "" : "s"}
      </p>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPage(Math.max(1, page - 1))}
          disabled={page <= 1}
        >
          <ChevronLeft className="h-4 w-4" /> Prev
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPage(Math.min(totalPages, page + 1))}
          disabled={page >= totalPages}
        >
          Next <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

function VehicleDrawer({ vehicle, onClose }: { vehicle: Vehicle | null; onClose: () => void }) {
  return (
    <Sheet open={!!vehicle} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full sm:max-w-md overflow-y-auto">
        {vehicle && (
          <>
            <SheetHeader>
              <div className="flex items-center gap-3">
                <div className="grid h-11 w-11 place-items-center rounded-xl bg-info/10 text-info">
                  <Truck className="h-5 w-5" />
                </div>
                <div className="min-w-0">
                  <SheetTitle className="truncate">{vehicle.name}</SheetTitle>
                  <SheetDescription>{vehicle.id}</SheetDescription>
                </div>
              </div>
            </SheetHeader>
            <div className="px-4 pb-6">
              <div className="mt-4 flex items-center justify-between rounded-lg border border-border bg-muted/40 px-3 py-2.5">
                <span className="text-xs text-muted-foreground">Current status</span>
                <StatusBadge tone={statusTone[vehicle.status]}>{vehicle.status}</StatusBadge>
              </div>

              <Separator className="my-5" />

              <dl className="space-y-3 text-sm">
                <Row label="Registration" value={<span className="font-mono">{vehicle.registration}</span>} />
                <Row label="Type" value={vehicle.type} />
                <Row label="Capacity" value={vehicle.capacity} />
                <Row label="Odometer" value={`${vehicle.odometer.toLocaleString()} km`} />
                <Row label="Last activity" value={vehicle.lastActivity} />
              </dl>
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
