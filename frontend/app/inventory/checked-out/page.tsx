"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { CheckCircle2, Loader2, RefreshCw } from "lucide-react";

import { AppShell, InfoCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";
import type { Device } from "@/types/device";
import type { OfficeInventory } from "@/types/inventory";

type CheckedOutRow = OfficeInventory & {
  device?: Device | null;
};

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function isOverdue(value?: string | null) {
  if (!value) {
    return false;
  }
  const date = new Date(value);
  return !Number.isNaN(date.getTime()) && date.getTime() < Date.now();
}

export default function CheckedOutPage() {
  const [rows, setRows] = useState<CheckedOutRow[]>([]);
  const [message, setMessage] = useState("Loading checked-out inventory...");
  const [loading, setLoading] = useState(true);
  const [actingId, setActingId] = useState<string | null>(null);

  async function loadRows() {
    if (!getStoredToken()) {
      setMessage("Sign in first to load checked-out inventory.");
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const inventoryRows = (await apiFetch("/inventory/checked-out")) as OfficeInventory[];
      const enrichedRows = await Promise.all(
        inventoryRows.map(async (row) => {
          try {
            const device = (await apiFetch(`/devices/${row.device_id}`)) as Device;
            return { ...row, device };
          } catch {
            return { ...row, device: null };
          }
        }),
      );
      setRows(enrichedRows);
      setMessage(enrichedRows.length ? `${enrichedRows.length} checked-out devices loaded.` : "No devices are currently checked out.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load checked-out inventory");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadRows();
  }, []);

  async function checkIn(row: CheckedOutRow) {
    setActingId(row.id);
    try {
      await apiFetch("/inventory/check-in", {
        method: "POST",
        body: JSON.stringify({
          device_id: row.device_id,
          notes: "Checked in from checked-out inventory page",
        }),
      });
      await loadRows();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to check in device");
    } finally {
      setActingId(null);
    }
  }

  return (
    <AppShell eyebrow="Inventory" title="Checked out" subtitle={message}>
      <InfoCard title="Loaned devices" description="Return tracking for inventory currently outside the IT office.">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-[#bdb4a8]">{rows.filter((row) => isOverdue(row.expected_return_at)).length} overdue</p>
          <button className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#171716] px-4 py-2 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45" onClick={() => void loadRows()} type="button">
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        <div className="space-y-3">
          {rows.length ? (
            rows.map((row) => {
              const label = row.device?.asset_tag ?? row.device?.display_name ?? row.device?.device_name ?? row.device_id;
              return (
                <div key={row.id} className="grid gap-4 rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-4 text-sm lg:grid-cols-[1.15fr_1fr_1fr_auto]">
                  <div>
                    <Link className="font-semibold text-[#d9ff3f] hover:text-[#efff7a]" href={`/devices/${row.device_id}`}>
                      {label}
                    </Link>
                    <p className="mt-1 text-[#9f968b]">{row.device?.serial_number ?? row.device?.model ?? "No serial/model recorded"}</p>
                  </div>
                  <div className="text-[#bdb4a8]">
                    <p>Borrower: <span className="text-white">{row.checked_out_to ?? row.assigned_user_name ?? "-"}</span></p>
                    <p>Email: <span className="text-white">{row.assigned_user_email ?? "-"}</span></p>
                  </div>
                  <div className="text-[#bdb4a8]">
                    <p>Checked out: <span className="text-white">{formatDate(row.checked_out_at)}</span></p>
                    <p className={isOverdue(row.expected_return_at) ? "text-[#f0d0ad]" : ""}>Return: <span className="text-white">{formatDate(row.expected_return_at)}</span></p>
                  </div>
                  <button
                    className="inline-flex h-11 items-center justify-center gap-2 rounded-full bg-[#d9ff3f] px-4 text-sm font-semibold text-[#151512] transition hover:bg-[#efff7a] disabled:cursor-not-allowed disabled:opacity-55"
                    disabled={actingId === row.id}
                    onClick={() => void checkIn(row)}
                    type="button"
                  >
                    {actingId === row.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                    Check in
                  </button>
                </div>
              );
            })
          ) : (
            <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-8 text-sm text-[#9f968b]">{message}</div>
          )}
        </div>
      </InfoCard>
    </AppShell>
  );
}
