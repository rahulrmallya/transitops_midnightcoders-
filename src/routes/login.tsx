import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState, type FormEvent } from "react";
import { AxiosError } from "axios";
import {
  Truck,
  Mail,
  Lock,
  ArrowRight,
  ShieldCheck,
  MapPin,
  Activity,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { useAuth } from "@/contexts/AuthContext";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign in — TransitOps" },
      {
        name: "description",
        content: "Sign in to TransitOps — smarter transport operations, one connected platform.",
      },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: isAuthLoading, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!isAuthLoading && isAuthenticated) {
      navigate({ to: "/dashboard", replace: true });
    }
  }, [isAuthenticated, isAuthLoading, navigate]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await login({ email, password });
    } catch (error) {
      const message = getAuthErrorMessage(error);
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid min-h-screen w-full grid-cols-1 lg:grid-cols-[1.05fr_1fr]">
      {/* Left: Brand panel */}
      <div className="relative hidden overflow-hidden bg-sidebar text-sidebar-foreground lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div
          className="pointer-events-none absolute inset-0 opacity-70"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 20%, oklch(0.3 0.05 265) 0%, transparent 50%), radial-gradient(circle at 80% 80%, oklch(0.35 0.07 45 / 0.35) 0%, transparent 55%)",
          }}
        />
        <div className="relative flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-lg bg-brand text-brand-foreground shadow-md">
            <Truck className="h-5 w-5" />
          </div>
          <div>
            <p className="text-base font-semibold text-white">TransitOps</p>
            <p className="text-xs text-sidebar-foreground/70">Transport Operations</p>
          </div>
        </div>

        <div className="relative max-w-md">
          <h1 className="text-4xl font-semibold leading-tight text-white">
            Smarter transport operations.{" "}
            <span className="text-brand">One connected platform.</span>
          </h1>
          <p className="mt-4 text-sm leading-relaxed text-sidebar-foreground/80">
            Command your entire fleet — vehicles, drivers, trips, maintenance and fuel — from
            a single operations cockpit designed for modern logistics teams.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {[
              { icon: MapPin, title: "Live fleet visibility", desc: "Track vehicles across depots" },
              { icon: Activity, title: "Ops in real time", desc: "Trips, fuel & maintenance" },
              { icon: ShieldCheck, title: "Driver compliance", desc: "Licences & safety scores" },
              { icon: Truck, title: "Utilization insights", desc: "Right-sized decisions" },
            ].map((f) => (
              <div
                key={f.title}
                className="rounded-xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm"
              >
                <f.icon className="h-4 w-4 text-brand" />
                <p className="mt-2 text-sm font-medium text-white">{f.title}</p>
                <p className="text-xs text-sidebar-foreground/70">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative flex items-center justify-between text-xs text-sidebar-foreground/60">
          <span>© {new Date().getFullYear()} TransitOps</span>
          <span>v1.0</span>
        </div>
      </div>

      {/* Right: Form */}
      <div className="flex items-center justify-center bg-background px-4 py-10 sm:px-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-8 flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-lg bg-primary text-primary-foreground">
              <Truck className="h-5 w-5" />
            </div>
            <div>
              <p className="text-base font-semibold">TransitOps</p>
              <p className="text-xs text-muted-foreground">Transport Operations</p>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">Welcome back</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Sign in to your operations workspace.
            </p>
          </div>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label htmlFor="email">Work email</Label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  className="h-11 pl-9"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <button
                  type="button"
                  className="text-xs font-medium text-brand hover:underline"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  className="h-11 pl-9"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            {errorMessage && (
              <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {errorMessage}
              </p>
            )}

            <label className="flex items-center gap-2 text-sm text-muted-foreground">
              <Checkbox id="remember" disabled={isSubmitting} />
              <span>Keep me signed in for 30 days</span>
            </label>

            <Button
              type="submit"
              disabled={isSubmitting}
              className="h-11 w-full bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {isSubmitting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <ArrowRight className="mr-2 h-4 w-4" />
              )}
              Sign in
            </Button>

            <p className="text-center text-xs text-muted-foreground">
              By continuing you agree to the TransitOps terms of service and privacy policy.
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}

interface ApiErrorResponse {
  message?: string;
  errors?: {
    details?: Array<{
      msg?: string;
    }>;
  };
}

function getAuthErrorMessage(error: unknown) {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiErrorResponse | undefined;
    const validationMessage = data?.errors?.details?.[0]?.msg;
    return validationMessage ?? data?.message ?? "Unable to sign in. Please try again.";
  }

  return "Unable to sign in. Please try again.";
}
