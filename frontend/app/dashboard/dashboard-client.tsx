"use client";

import { useEffect, useState } from "react";

import { AppShell, InfoCard, MetricCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { clearStoredToken, getStoredToken } from "@/lib/auth-store";

export function DashboardClient() {
  const [summary, setSummary] = useState<{
    total_devices: number;
    in_office: number;
    checked_out: number;
    under_repair: number;
    missing: number;
    open_conflicts: number;
    last_servicenow_import: string | null;
    last_intune_sync: string | null;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setError("No session token found. Sign in first.");
      return;
    }

    apiFetch("/reports/dashboard-summary")
      .then(setSummary)
      .catch((fetchError: unknown) => {
        setError(fetchError instanceof Error ? fetchError.message : "Unable to load dashboard data");
      });
  }, []);

  return (
    <AppShell eyebrow="Overview" title="Dashboard" subtitle="A live command center for office inventory, imports, syncs, and conflict review.">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total devices" value={summary ? String(summary.total_devices) : "..."} tone="accent" detail="Master inventory across laptops, desktops, monitors, and accessories." />
        <MetricCard label="In office" value={summary ? String(summary.in_office) : "..."} tone="neutral" detail="Physical inventory currently checked into the IT office." />
        <MetricCard label="Checked out" value={summary ? String(summary.checked_out) : "..."} tone="alert" detail="Devices assigned to staff or out for field support." />
        <MetricCard label="Open conflicts" value={summary ? String(summary.open_conflicts) : "..."} tone="alert" detail="ServiceNow, Intune, local inventory, and OCR disagree on one or more fields." />
      </div>

      {error ? <p className="mt-4 rounded-[1.15rem] border border-[#caa57f]/40 bg-[#2d241c] p-4 text-sm text-[#f0d0ad]">{error}</p> : null}

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <InfoCard title="Today at a glance" description="Fast access to the highest-signal operational numbers.">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">Last ServiceNow import</p>
              <p className="mt-2 text-lg font-medium text-white">{summary?.last_servicenow_import ?? "Unavailable"}</p>
            </div>
            <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">Last Intune sync</p>
              <p className="mt-2 text-lg font-medium text-white">{summary?.last_intune_sync ?? "Unavailable"}</p>
            </div>
          </div>
        </InfoCard>

        <InfoCard title="Session" description="Use the same browser session to reach authenticated backend endpoints.">
          <div className="space-y-3 text-sm leading-6 text-[#bdb4a8]">
            <p>{getStoredToken() ? "Authenticated session token detected." : "No token stored."}</p>
            <button className="rounded-full border border-white/10 bg-[#171716] px-5 py-3 font-semibold text-white transition hover:border-[#d9ff3f]/40" onClick={() => clearStoredToken()} type="button">
              Clear token
            </button>
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
