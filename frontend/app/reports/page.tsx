"use client";

import { useEffect, useMemo, useState } from "react";
import { Download, Loader2, RefreshCw } from "lucide-react";

import { AppShell, InfoCard, MetricCard } from "@/components/app-shell";
import { apiFetch, apiText } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";

type ReportDefinition = {
  key: string;
  label: string;
  path: string;
};

const reports: ReportDefinition[] = [
  { key: "office-inventory", label: "Office inventory", path: "/reports/office-inventory" },
  { key: "checked-out", label: "Checked out", path: "/reports/checked-out" },
  { key: "overdue", label: "Overdue loaners", path: "/reports/overdue" },
  { key: "missing", label: "Missing devices", path: "/reports/missing" },
  { key: "servicenow-not-intune", label: "ServiceNow not Intune", path: "/reports/servicenow-not-intune" },
  { key: "intune-not-servicenow", label: "Intune not ServiceNow", path: "/reports/intune-not-servicenow" },
  { key: "conflicts", label: "Open conflicts", path: "/reports/conflicts" },
  { key: "inventory-events", label: "Inventory events", path: "/reports/inventory-events" },
];

function asRows(payload: unknown): Record<string, unknown>[] {
  if (Array.isArray(payload)) {
    return payload.filter((row): row is Record<string, unknown> => typeof row === "object" && row !== null);
  }
  if (typeof payload === "object" && payload !== null) {
    return Object.entries(payload).map(([metric, value]) => ({ metric, value }));
  }
  return [];
}

function valueText(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

export default function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState(reports[0]);
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null);
  const [message, setMessage] = useState("Loading report data...");
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const columns = useMemo(() => {
    const keys = new Set<string>();
    rows.slice(0, 25).forEach((row) => Object.keys(row).forEach((key) => keys.add(key)));
    return Array.from(keys).slice(0, 12);
  }, [rows]);

  async function loadReport(report = selectedReport) {
    if (!getStoredToken()) {
      setMessage("Sign in first to load reports.");
      return;
    }

    setLoading(true);
    try {
      const [reportPayload, summaryPayload] = await Promise.all([
        apiFetch(report.path),
        apiFetch("/reports/dashboard-summary"),
      ]);
      const nextRows = asRows(reportPayload);
      setRows(nextRows);
      setSummary(summaryPayload as Record<string, unknown>);
      setMessage(`${report.label}: ${nextRows.length} rows loaded.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load report");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadReport(selectedReport);
  }, [selectedReport]);

  async function downloadCsv() {
    setDownloading(true);
    try {
      const csv = await apiText("/reports/export/csv");
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "it-inventory-export.csv";
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to download CSV");
    } finally {
      setDownloading(false);
    }
  }

  return (
    <AppShell eyebrow="Reporting" title="Reports" subtitle={message}>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total devices" value={valueText(summary?.total_devices)} tone="accent" detail="Master device records." />
        <MetricCard label="Checked out" value={valueText(summary?.checked_out)} tone="neutral" detail="Devices currently assigned out." />
        <MetricCard label="Missing" value={valueText(summary?.missing)} tone="alert" detail="Devices marked missing." />
        <MetricCard label="Open conflicts" value={valueText(summary?.open_conflicts)} tone="alert" detail="Rows needing review." />
      </div>

      <div className="mt-6">
        <InfoCard title="Report explorer" description="Choose a report and inspect live rows from the backend.">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {reports.map((report) => (
                <button
                  className={`rounded-full px-4 py-2 text-sm font-semibold transition ${selectedReport.key === report.key ? "bg-[#d9ff3f] text-[#151512]" : "border border-white/10 bg-[#171716] text-white hover:border-[#d9ff3f]/45"}`}
                  key={report.key}
                  onClick={() => setSelectedReport(report)}
                  type="button"
                >
                  {report.label}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <button className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#171716] px-4 py-2 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45" onClick={() => void loadReport()} type="button">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                Refresh
              </button>
              <button className="inline-flex items-center gap-2 rounded-full bg-[#d9ff3f] px-4 py-2 text-sm font-semibold text-[#151512] transition hover:bg-[#efff7a]" onClick={() => void downloadCsv()} type="button">
                {downloading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                Export CSV
              </button>
            </div>
          </div>

          <div className="overflow-x-auto rounded-[1.15rem] border border-white/10">
            {rows.length && columns.length ? (
              <table className="min-w-full table-fixed text-left text-sm">
                <thead className="bg-[#171716] text-xs uppercase tracking-[0.18em] text-[#9f968b]">
                  <tr>
                    {columns.map((column) => (
                      <th className="w-48 px-4 py-3 font-medium" key={column}>{column}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, rowIndex) => (
                    <tr className={rowIndex % 2 === 0 ? "bg-[#20201d]" : "bg-[#282721]"} key={`${selectedReport.key}-${rowIndex}`}>
                      {columns.map((column) => (
                        <td className="w-48 truncate px-4 py-4 text-[#bdb4a8]" key={column} title={valueText(row[column])}>
                          {valueText(row[column])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="px-4 py-8 text-sm text-[#9f968b]">{loading ? "Loading report rows..." : "No rows returned for this report."}</div>
            )}
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
