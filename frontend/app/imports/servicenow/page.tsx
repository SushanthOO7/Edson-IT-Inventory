"use client";

import { MailCheck, RefreshCw, Search } from "lucide-react";
import { useEffect, useState } from "react";

import { AppShell, InfoCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";

type ServiceNowImportResponse = {
  run_id: string;
  status: string;
  total_rows: number;
  created_devices: number;
  updated_devices: number;
  matched_devices: number;
  conflicts_created: number;
};

type ImportRun = {
  id: string;
  source: string;
  started_at?: string | null;
  finished_at?: string | null;
  status: string;
  file_name?: string | null;
  email_subject?: string | null;
  email_received_at?: string | null;
  total_rows: number;
  created_devices: number;
  updated_devices: number;
  matched_devices: number;
  conflicts_created: number;
  errors_count: number;
  created_at: string;
};

type ServiceNowAsset = {
  id: string;
  asset_tag?: string | null;
  model_category?: string | null;
  display_name?: string | null;
  u_assigned_to?: string | null;
  assigned_to?: string | null;
  u_cost_center?: string | null;
  install_status?: string | null;
  serial_number?: string | null;
  u_mac_address?: string | null;
  ci?: string | null;
  comments?: string | null;
  department?: string | null;
  imported_at?: string | null;
  import_run_id?: string | null;
  raw_json?: Record<string, unknown> | null;
};

type AssetListResponse = {
  items: ServiceNowAsset[];
  total: number;
  limit: number;
  offset: number;
  columns: string[];
  filters: {
    departments: string[];
    install_statuses: string[];
    model_categories: string[];
    assigned_to: string[];
  };
};

const fallbackColumns = [
  "asset_tag",
  "model_category",
  "display_name",
  "u_assigned_to",
  "assigned_to",
  "u_cost_center",
  "install_status",
  "serial_number",
  "u_mac_address",
  "ci",
  "comments",
  "department",
];

function formatDate(value?: string | null) {
  if (!value) {
    return "Unavailable";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function fieldValue(asset: ServiceNowAsset, column: string) {
  const rawValue = asset.raw_json?.[column];
  const value = rawValue ?? asset[column as keyof ServiceNowAsset];
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  return typeof value === "object" ? JSON.stringify(value) : String(value);
}

export default function ServiceNowImportPage() {
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(true);
  const [result, setResult] = useState<ServiceNowImportResponse | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [runs, setRuns] = useState<ImportRun[]>([]);
  const [assetResponse, setAssetResponse] = useState<AssetListResponse | null>(null);
  const [searchInput, setSearchInput] = useState("");
  const [query, setQuery] = useState("");
  const [department, setDepartment] = useState("");
  const [installStatus, setInstallStatus] = useState("");
  const [modelCategory, setModelCategory] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  const [limit, setLimit] = useState(100);
  const [offset, setOffset] = useState(0);

  async function loadData() {
    setRefreshing(true);
    try {
      const params = new URLSearchParams({
        limit: String(limit),
        offset: String(offset),
      });
      if (query) params.set("q", query);
      if (department) params.set("department", department);
      if (installStatus) params.set("install_status", installStatus);
      if (modelCategory) params.set("model_category", modelCategory);
      if (assignedTo) params.set("assigned_to", assignedTo);

      const [history, assets] = await Promise.all([
        apiFetch("/imports/servicenow/history?limit=8"),
        apiFetch(`/imports/servicenow/assets?${params.toString()}`),
      ]);
      setRuns(history as ImportRun[]);
      setAssetResponse(assets as AssetListResponse);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load ServiceNow sync data");
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    if (!getStoredToken()) {
      setMessage("Sign in first to sync ServiceNow email data.");
      setRefreshing(false);
      return;
    }

    void loadData();
  }, [query, department, installStatus, modelCategory, assignedTo, limit, offset]);

  async function syncLatestEmail() {
    setLoading(true);
    setMessage(null);
    setResult(null);

    try {
      const response = await apiFetch("/imports/servicenow/from-email?force=true", { method: "POST" });
      setResult(response as ServiceNowImportResponse);
      setMessage("Latest ServiceNow email synced.");
      setOffset(0);
      await loadData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to sync latest email");
    } finally {
      setLoading(false);
    }
  }

  function applySearch() {
    setOffset(0);
    setQuery(searchInput.trim());
  }

  function resetFilters() {
    setSearchInput("");
    setQuery("");
    setDepartment("");
    setInstallStatus("");
    setModelCategory("");
    setAssignedTo("");
    setOffset(0);
  }

  const latestRun = runs[0];
  const totalAssets = assetResponse?.total ?? 0;
  const assets = assetResponse?.items ?? [];
  const columns = assetResponse?.columns.length ? assetResponse.columns : fallbackColumns;
  const pageStart = totalAssets ? offset + 1 : 0;
  const pageEnd = Math.min(offset + limit, totalAssets);
  const canGoBack = offset > 0;
  const canGoForward = offset + limit < totalAssets;

  return (
    <AppShell eyebrow="Imports" title="ServiceNow email sync" subtitle="Latest CSV rows from the configured mailbox, searchable across all loaded ServiceNow device snapshots.">
      <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <InfoCard title="Mailbox sync" description={latestRun ? `Last run: ${formatDate(latestRun.finished_at ?? latestRun.created_at)}` : "No ServiceNow email import has completed yet."}>
          <div className="space-y-4 text-sm leading-6 text-[#bdb4a8]">
            <div className="flex flex-wrap items-center gap-3">
              <button className="inline-flex items-center gap-2 rounded-full bg-[#d9ff3f] px-5 py-3 font-semibold text-[#151512] transition hover:bg-[#efff7a] disabled:cursor-not-allowed disabled:opacity-60" disabled={loading || refreshing} onClick={syncLatestEmail} type="button">
                {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <MailCheck className="h-4 w-4" />}
                {loading ? "Syncing" : "Sync latest email"}
              </button>
              <button className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#171716] px-5 py-3 font-semibold text-white transition hover:border-[#d9ff3f]/40 disabled:cursor-not-allowed disabled:opacity-60" disabled={loading || refreshing} onClick={() => void loadData()} type="button">
                <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
                Refresh
              </button>
            </div>

            {message ? <p className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4 text-white">{message}</p> : null}

            {result ? (
              <div className="grid gap-3 sm:grid-cols-2">
                <p>Rows: <span className="text-white">{result.total_rows}</span></p>
                <p>Created devices: <span className="text-white">{result.created_devices}</span></p>
                <p>Updated snapshots: <span className="text-white">{result.updated_devices}</span></p>
                <p>Conflicts: <span className="text-white">{result.conflicts_created}</span></p>
              </div>
            ) : null}

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">Assets</p>
                <p className="mt-2 text-2xl font-semibold text-white">{totalAssets}</p>
              </div>
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">CSV columns</p>
                <p className="mt-2 text-2xl font-semibold text-white">{columns.length}</p>
              </div>
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9f968b]">Last rows</p>
                <p className="mt-2 text-2xl font-semibold text-white">{latestRun?.total_rows ?? 0}</p>
              </div>
            </div>
          </div>
        </InfoCard>

        <InfoCard title="Recent imports" description={latestRun?.email_subject ?? latestRun?.file_name ?? "Waiting for the first email sync."}>
          <div className="overflow-hidden rounded-[1.15rem] border border-white/10">
            {runs.length ? (
              runs.map((run, index) => (
                <div key={run.id} className={`grid gap-3 px-4 py-4 text-sm md:grid-cols-[1.2fr_0.7fr_0.5fr_0.5fr] ${index % 2 === 0 ? "bg-[#171716]" : "bg-[#2a2925]"}`}>
                  <div>
                    <p className="font-medium text-white">{run.email_subject ?? run.file_name ?? run.source}</p>
                    <p className="mt-1 text-xs text-[#9f968b]">{formatDate(run.email_received_at ?? run.created_at)}</p>
                  </div>
                  <p className="text-[#bdb4a8]">{run.status}</p>
                  <p className="text-[#bdb4a8]">{run.total_rows} rows</p>
                  <p className="text-right text-[#bdb4a8]">{run.conflicts_created} conflicts</p>
                </div>
              ))
            ) : (
              <div className="px-4 py-8 text-sm text-[#9f968b]">{refreshing ? "Loading imports..." : "No imports found."}</div>
            )}
          </div>
        </InfoCard>
      </div>

      <div className="mt-6">
        <InfoCard title="Search and filters" description={`Showing ${pageStart}-${pageEnd} of ${totalAssets} ServiceNow device rows.`}>
          <div className="grid gap-3 xl:grid-cols-[1.4fr_repeat(4,1fr)_auto]">
            <label className="relative block">
              <Search className="pointer-events-none absolute left-3 top-3.5 h-4 w-4 text-[#9f968b]" />
              <input
                className="h-12 w-full rounded-full border border-white/10 bg-[#171716] pl-10 pr-3 text-sm text-white outline-none transition placeholder:text-[#6f675e] focus:border-[#d9ff3f]/60"
                onChange={(event) => setSearchInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") applySearch();
                }}
                placeholder="Search asset, serial, user, department, CI"
                value={searchInput}
              />
            </label>
            <select className="h-12 rounded-full border border-white/10 bg-[#171716] px-3 text-sm text-white outline-none focus:border-[#d9ff3f]/60" onChange={(event) => { setDepartment(event.target.value); setOffset(0); }} value={department}>
              <option value="">All departments</option>
              {(assetResponse?.filters.departments ?? []).map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select className="h-12 rounded-full border border-white/10 bg-[#171716] px-3 text-sm text-white outline-none focus:border-[#d9ff3f]/60" onChange={(event) => { setInstallStatus(event.target.value); setOffset(0); }} value={installStatus}>
              <option value="">All statuses</option>
              {(assetResponse?.filters.install_statuses ?? []).map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select className="h-12 rounded-full border border-white/10 bg-[#171716] px-3 text-sm text-white outline-none focus:border-[#d9ff3f]/60" onChange={(event) => { setModelCategory(event.target.value); setOffset(0); }} value={modelCategory}>
              <option value="">All models</option>
              {(assetResponse?.filters.model_categories ?? []).map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select className="h-12 rounded-full border border-white/10 bg-[#171716] px-3 text-sm text-white outline-none focus:border-[#d9ff3f]/60" onChange={(event) => { setAssignedTo(event.target.value); setOffset(0); }} value={assignedTo}>
              <option value="">All users</option>
              {(assetResponse?.filters.assigned_to ?? []).map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <div className="flex gap-2">
              <button className="h-12 rounded-full bg-[#d9ff3f] px-4 text-sm font-semibold text-[#151512] transition hover:bg-[#efff7a]" onClick={applySearch} type="button">Search</button>
              <button className="h-12 rounded-full border border-white/10 bg-[#171716] px-4 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/40" onClick={resetFilters} type="button">Reset</button>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-[#bdb4a8]">
            <div className="flex flex-wrap gap-2">
              {columns.map((column) => (
                <span key={column} className="rounded-full border border-white/10 bg-[#171716] px-3 py-1 text-xs text-[#bdb4a8]">{column}</span>
              ))}
            </div>
            <select className="h-10 rounded-full border border-white/10 bg-[#171716] px-3 text-sm text-white outline-none focus:border-[#d9ff3f]/60" onChange={(event) => { setLimit(Number(event.target.value)); setOffset(0); }} value={limit}>
              {[50, 100, 250, 500].map((value) => <option key={value} value={value}>{value} / page</option>)}
            </select>
          </div>
        </InfoCard>
      </div>

      <div className="mt-6">
        <InfoCard title="Loaded ServiceNow devices" description={`${totalAssets} imported device snapshots from ServiceNow CSV data.`}>
          <div className="overflow-x-auto rounded-[1.15rem] border border-white/10">
            <table className="table-fixed text-left text-sm" style={{ minWidth: `${Math.max(columns.length, 6) * 12}rem` }}>
              <thead className="bg-[#171716] text-xs uppercase tracking-[0.18em] text-[#9f968b]">
                <tr>
                  {columns.map((column) => (
                    <th key={column} className="w-48 px-4 py-3 font-medium">{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {assets.length ? (
                  assets.map((asset, rowIndex) => (
                    <tr key={asset.id} className={rowIndex % 2 === 0 ? "bg-[#20201d]" : "bg-[#282721]"}>
                      {columns.map((column) => (
                        <td key={`${asset.id}-${column}`} className="w-48 truncate px-4 py-4 text-[#bdb4a8]" title={fieldValue(asset, column)}>
                          {column === "asset_tag" ? <span className="font-medium text-[#d9ff3f]">{fieldValue(asset, column)}</span> : fieldValue(asset, column)}
                        </td>
                      ))}
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="px-4 py-8 text-[#9f968b]" colSpan={columns.length}>{refreshing ? "Loading assets..." : "No ServiceNow assets match the current filters."}</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-[#bdb4a8]">
            <span>Showing {pageStart}-{pageEnd} of {totalAssets}</span>
            <div className="flex gap-2">
              <button className="rounded-full border border-white/10 bg-[#171716] px-4 py-2 text-white transition hover:border-[#d9ff3f]/40 disabled:cursor-not-allowed disabled:opacity-50" disabled={!canGoBack || refreshing} onClick={() => setOffset(Math.max(0, offset - limit))} type="button">Previous</button>
              <button className="rounded-full border border-white/10 bg-[#171716] px-4 py-2 text-white transition hover:border-[#d9ff3f]/40 disabled:cursor-not-allowed disabled:opacity-50" disabled={!canGoForward || refreshing} onClick={() => setOffset(offset + limit)} type="button">Next</button>
            </div>
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
