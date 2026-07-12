import { createFileRoute } from "@tanstack/react-router";
import {
  Truck,
  CheckCircle2,
  Route as RouteIcon,
  Gauge,
  Users,
  Wrench,
  Circle,
  ArrowUpRight,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { PageHeader } from "@/components/PageHeader";
import { StatsCard } from "@/components/StatsCard";
import { SectionTitle } from "@/components/SectionTitle";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/StatusBadge";
import {
  fleetHealth,
  fleetUtilization,
  operationalActivity,
  recentActivity,
  vehicleStatusMix,
} from "@/store/sample-data";

export const Route = createFileRoute("/_app/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — TransitOps" },
      { name: "description", content: "Fleet-wide KPIs, utilization and operational activity." },
    ],
  }),
  component: DashboardPage,
});

const statusColorVars: Record<string, string> = {
  available: "var(--success)",
  ontrip: "var(--info)",
  maintenance: "var(--brand)",
  retired: "var(--slate-muted)",
};

function toneToBadge(tone: "success" | "warning" | "info" | "brand") {
  return tone === "warning" ? "warning" : tone;
}

function DashboardPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Fleet Overview"
        description="Real-time snapshot of vehicles, drivers and operations across your fleet."
        actions={
          <>
            <Button variant="outline" size="sm" className="hidden sm:inline-flex">
              Last 7 days
            </Button>
            <Button size="sm" className="bg-brand text-brand-foreground hover:bg-brand/90">
              New trip
            </Button>
          </>
        }
      />

      {/* KPI grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatsCard label="Total Vehicles" value={128} icon={Truck} tone="info" delta={{ value: "+4", direction: "up" }} hint="Across 3 depots" />
        <StatsCard label="Available Vehicles" value={84} icon={CheckCircle2} tone="success" delta={{ value: "+6", direction: "up" }} />
        <StatsCard label="Active Trips" value={24} icon={RouteIcon} tone="brand" delta={{ value: "-2", direction: "down" }} />
        <StatsCard label="Fleet Utilization" value="78%" icon={Gauge} tone="analytics" delta={{ value: "+3.2%", direction: "up" }} />
        <StatsCard label="Drivers On Duty" value={62} icon={Users} tone="cyan" hint="of 96 active" />
        <StatsCard label="In Maintenance" value={9} icon={Wrench} tone="warning" delta={{ value: "+1", direction: "up" }} />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardContent className="p-5">
            <SectionTitle
              title="Fleet Utilization"
              description="9-month utilization trend across active fleet"
            />
            <div className="mt-4 h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={fleetUtilization} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <defs>
                    <linearGradient id="utilFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="month" stroke="var(--muted-foreground)" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--muted-foreground)" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: 10,
                      fontSize: 12,
                      color: "var(--popover-foreground)",
                    }}
                  />
                  <Area type="monotone" dataKey="utilization" stroke="var(--chart-1)" strokeWidth={2.5} fill="url(#utilFill)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <SectionTitle title="Vehicle Status" description="Current fleet distribution" />
            <div className="mt-4 h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={vehicleStatusMix}
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                    nameKey="name"
                    stroke="var(--card)"
                    strokeWidth={2}
                  >
                    {vehicleStatusMix.map((entry) => (
                      <Cell key={entry.key} fill={statusColorVars[entry.key]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: 10,
                      fontSize: 12,
                      color: "var(--popover-foreground)",
                    }}
                  />
                  <Legend
                    iconType="circle"
                    iconSize={8}
                    wrapperStyle={{ fontSize: 12, color: "var(--muted-foreground)" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardContent className="p-5">
            <SectionTitle title="Operational Activity" description="Trips completed vs fuel refills, last 7 days" />
            <div className="mt-4 h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={operationalActivity} margin={{ top: 8, right: 8, left: -16, bottom: 0 }} barCategoryGap={16}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="day" stroke="var(--muted-foreground)" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--muted-foreground)" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    cursor={{ fill: "var(--muted)", opacity: 0.5 }}
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: 10,
                      fontSize: 12,
                      color: "var(--popover-foreground)",
                    }}
                  />
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12, color: "var(--muted-foreground)" }} />
                  <Bar dataKey="trips" name="Trips" fill="var(--chart-1)" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="fuel" name="Fuel refills" fill="var(--chart-3)" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <SectionTitle title="Fleet Health" description="At-a-glance system status" />
            <ul className="mt-4 space-y-3">
              {fleetHealth.map((item) => (
                <li
                  key={item.label}
                  className="flex items-center justify-between rounded-lg border border-border bg-background/50 px-3 py-2.5"
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`grid h-8 w-8 place-items-center rounded-md ${
                        item.tone === "success"
                          ? "bg-success/12 text-success"
                          : item.tone === "warning"
                            ? "bg-warning/20 text-warning"
                            : item.tone === "destructive"
                              ? "bg-destructive/12 text-destructive"
                              : "bg-info/12 text-info"
                      }`}
                    >
                      <Circle className="h-3 w-3 fill-current" />
                    </span>
                    <span className="text-sm text-foreground">{item.label}</span>
                  </div>
                  <span className="text-sm font-semibold tabular-nums">{item.value}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Recent activity */}
      <Card>
        <CardContent className="p-5">
          <SectionTitle
            title="Recent Activity"
            description="Latest events across your fleet"
            action={
              <Button variant="ghost" size="sm" className="text-brand hover:text-brand">
                View all
                <ArrowUpRight className="ml-1 h-3.5 w-3.5" />
              </Button>
            }
          />
          <ul className="mt-4 divide-y divide-border">
            {recentActivity.map((item) => (
              <li key={item.id} className="flex items-center justify-between gap-4 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-foreground">{item.title}</p>
                  <p className="truncate text-xs text-muted-foreground">{item.meta}</p>
                </div>
                <StatusBadge tone={toneToBadge(item.tone)} dot>
                  {item.tone === "success"
                    ? "Completed"
                    : item.tone === "warning"
                      ? "Attention"
                      : item.tone === "info"
                        ? "In progress"
                        : "Logged"}
                </StatusBadge>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
