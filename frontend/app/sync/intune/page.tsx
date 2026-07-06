"use client";

import { FormEvent, useEffect, useState } from "react";
import { Loader2, RefreshCw, Wifi } from "lucide-react";

import { AppShell, InfoCard, MetricCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";

type SyncRun = {
  id: string;
  source: string;
  started_at?: string | null;
  finished_at?: string | null;
  status: string;
  total_records: number;
  matched_devices: number;
  created_devices: number;
  conflicts_created: number;
  errors_count: number;
  error_log?: Record<string, unknown> | null;
};

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export default function IntuneSyncPage() {
  const [bearerToken, setBearerToken] = useState("");
  const [graphUrl, setGraphUrl] = useState("");
  const [runs, setRuns] = useState<SyncRun[]>([]);
  const [result, setResult] = useState<SyncRun | null>(null);
  const [message, setMessage] = useState("Ready to sync managed devices from Microsoft Graph.");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  async function loadHistory() {
    if (!getStoredToken()) {
      setMessage("Sign in first to sync Intune devices.");
      return;
    }

    setRefreshing(true);
    try {
      const response = (await apiFetch("/sync/intune/history")) as SyncRun[];
      setRuns(response);
      if (!result && response[0]) {
        setResult(response[0]);
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load Intune sync history");
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void loadHistory();
  }, []);

  async function submitSync(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!bearerToken.trim()) {
      setMessage("Paste a Microsoft Graph bearer token first.");
      return;
    }

    setLoading(true);
    setMessage("Syncing Intune devices...");
    try {
      const response = (await apiFetch("/sync/intune", {
        method: "POST",
        body: JSON.stringify({
          bearer_token: bearerToken,
          graph_url: graphUrl.trim() || null,
        }),
      })) as SyncRun;
      setResult(response);
      setBearerToken("");
      setMessage(`Intune sync ${response.status.toLowerCase()}: ${response.total_records} records processed.`);
      await loadHistory();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Intune sync failed");
    } finally {
      setLoading(false);
    }
  }

  const latest = result ?? runs[0] ?? null;

  return (
    <AppShell eyebrow="Sync" title="Intune sync" subtitle={message}>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Last status" value={latest?.status ?? "-"} tone={latest?.status === "FAILED" ? "alert" : "accent"} detail={formatDate(latest?.finished_at ?? latest?.started_at)} />
        <MetricCard label="Records" value={String(latest?.total_records ?? 0)} tone="neutral" detail="Managed devices returned by Graph." />
        <MetricCard label="Matched" value={String(latest?.matched_devices ?? 0)} tone="neutral" detail="Existing inventory records linked." />
        <MetricCard label="Created" value={String(latest?.created_devices ?? 0)} tone="alert" detail="New inventory records from Intune." />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <InfoCard title="Run sync" description="The bearer token is sent once to the backend and is not stored.">
          <form className="space-y-4" onSubmit={submitSync}>
            <label className="block">
              <span className="mb-2 block text-sm text-[#bdb4a8]">Bearer token</span>
              <textarea
                className="min-h-32 w-full resize-y rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-3 text-sm leading-6 text-white outline-none placeholder:text-[#6f675e] focus:border-[#d9ff3f]/60"
                onChange={(event) => setBearerToken(event.target.value)}
                placeholder="Paste Graph access token"
                value={bearerToken}
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm text-[#bdb4a8]">Graph URL</span>
              <input
                className="h-12 w-full rounded-full border border-white/10 bg-[#171716] px-4 text-sm text-white outline-none placeholder:text-[#6f675e] focus:border-[#d9ff3f]/60"
                onChange={(event) => setGraphUrl(event.target.value)}
                placeholder="Default managedDevices endpoint"
                value={graphUrl}
              />
            </label>
            <div className="flex flex-wrap gap-3">
              <button className="inline-flex items-center gap-2 rounded-full bg-[#d9ff3f] px-5 py-3 text-sm font-semibold text-[#151512] transition hover:bg-[#efff7a] disabled:cursor-not-allowed disabled:opacity-60" disabled={loading} type="submit">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wifi className="h-4 w-4" />}
                Sync Intune
              </button>
              <button className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#171716] px-5 py-3 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45" onClick={() => void loadHistory()} type="button">
                <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
                Refresh history
              </button>
            </div>
          </form>
        </InfoCard>

        <InfoCard title="Sync history" description={`${runs.length} Intune sync runs loaded.`}>
          <div className="space-y-3">
            {runs.length ? (
              runs.map((run) => (
                <button
                  className="grid w-full gap-3 rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-4 text-left text-sm transition hover:border-[#d9ff3f]/45 md:grid-cols-[1fr_0.6fr_0.6fr_0.6fr]"
                  key={run.id}
                  onClick={() => setResult(run)}
                  type="button"
                >
                  <div>
                    <p className="font-semibold text-white">{run.status}</p>
                    <p className="mt-1 text-xs text-[#9f968b]">{formatDate(run.finished_at ?? run.started_at)}</p>
                  </div>
                  <p className="text-[#bdb4a8]">{run.total_records} records</p>
                  <p className="text-[#bdb4a8]">{run.matched_devices} matched</p>
                  <p className="text-[#bdb4a8]">{run.conflicts_created} conflicts</p>
                </button>
              ))
            ) : (
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-8 text-sm text-[#9f968b]">{refreshing ? "Loading history..." : "No Intune sync runs found."}</div>
            )}
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
