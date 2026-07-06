"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { RefreshCw, Search } from "lucide-react";

import { AppShell, InfoCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";
import type { Device } from "@/types/device";

type DeviceListResponse = {
  items: Device[];
  total: number;
};

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [message, setMessage] = useState<string>("Loading device list...");
  const [searchInput, setSearchInput] = useState("");
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  async function loadDevices() {
    if (!getStoredToken()) {
      setMessage("Sign in first to load live devices.");
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: String(limit),
        offset: String(offset),
      });
      if (query) {
        params.set("q", query);
      }
      const response = (await apiFetch(`/devices?${params.toString()}`)) as DeviceListResponse;
      setDevices(response.items);
      setTotal(response.total);
      setMessage(response.items.length ? `Showing ${offset + 1}-${Math.min(offset + limit, response.total)} of ${response.total} devices.` : "No devices match the current search.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load device list");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDevices();
  }, [query, limit, offset]);

  function applySearch() {
    setOffset(0);
    setQuery(searchInput.trim());
  }

  function resetSearch() {
    setSearchInput("");
    setQuery("");
    setOffset(0);
  }

  const canGoBack = offset > 0;
  const canGoForward = offset + limit < total;

  return (
    <AppShell eyebrow="Inventory" title="Devices" subtitle={message}>
      <InfoCard title="Device list" description="Search and page through the master inventory records.">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex min-w-[min(100%,36rem)] flex-1 flex-wrap gap-2">
            <label className="relative min-w-[16rem] flex-1">
              <Search className="pointer-events-none absolute left-3 top-3.5 h-4 w-4 text-[#9f968b]" />
              <input
                className="h-12 w-full rounded-full border border-white/10 bg-[#171716] pl-10 pr-3 text-sm text-white outline-none transition placeholder:text-[#6f675e] focus:border-[#d9ff3f]/60"
                onChange={(event) => setSearchInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") applySearch();
                }}
                placeholder="Search asset, serial, name, model"
                value={searchInput}
              />
            </label>
            <button className="h-12 rounded-full bg-[#d9ff3f] px-5 text-sm font-semibold text-[#151512] transition hover:bg-[#efff7a]" onClick={applySearch} type="button">Search</button>
            <button className="h-12 rounded-full border border-white/10 bg-[#171716] px-5 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45" onClick={resetSearch} type="button">Reset</button>
          </div>
          <div className="flex gap-2">
            <select className="h-12 rounded-full border border-white/10 bg-[#171716] px-3 text-sm text-white outline-none focus:border-[#d9ff3f]/60" onChange={(event) => { setLimit(Number(event.target.value)); setOffset(0); }} value={limit}>
              {[25, 50, 100].map((value) => <option key={value} value={value}>{value} / page</option>)}
            </select>
            <button className="grid h-12 w-12 place-items-center rounded-full border border-white/10 bg-[#171716] text-white transition hover:border-[#d9ff3f]/45" onClick={() => void loadDevices()} type="button" title="Refresh">
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        <div className="overflow-hidden rounded-[1.15rem] border border-white/10">
          {devices.length ? (
            devices.map((device, index) => (
              <div key={device.id} className={`grid gap-4 px-4 py-4 text-sm md:grid-cols-[1fr_1.4fr_0.8fr_0.9fr_0.5fr] ${index % 2 === 0 ? "bg-[#171716]" : "bg-[#2a2925]"}`}>
                <Link className="font-medium text-[#d9ff3f] hover:text-[#efff7a]" href={`/devices/${device.id}`}>
                  {device.asset_tag ?? device.serial_number ?? "Unknown"}
                </Link>
                <div className="text-white">{device.display_name ?? device.device_name ?? "Unnamed device"}</div>
                <div className="text-[#bdb4a8]">{device.lifecycle_status}</div>
                <div className="text-[#bdb4a8]">{device.department ?? device.model ?? "Unassigned"}</div>
                <div className="text-right text-[#9f968b]">{Math.round(device.source_confidence)}%</div>
              </div>
            ))
          ) : (
            <div className="px-4 py-8 text-sm text-[#9f968b]">{message}</div>
          )}
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-[#bdb4a8]">
          <span>{total ? `Showing ${offset + 1}-${Math.min(offset + limit, total)} of ${total}` : "No devices"}</span>
          <div className="flex gap-2">
            <button className="rounded-full border border-white/10 bg-[#171716] px-4 py-2 text-white transition hover:border-[#d9ff3f]/40 disabled:cursor-not-allowed disabled:opacity-50" disabled={!canGoBack || loading} onClick={() => setOffset(Math.max(0, offset - limit))} type="button">Previous</button>
            <button className="rounded-full border border-white/10 bg-[#171716] px-4 py-2 text-white transition hover:border-[#d9ff3f]/40 disabled:cursor-not-allowed disabled:opacity-50" disabled={!canGoForward || loading} onClick={() => setOffset(offset + limit)} type="button">Next</button>
          </div>
        </div>
      </InfoCard>
    </AppShell>
  );
}
