"use client";

import { useEffect, useState } from "react";

import { AppShell, InfoCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";
import type { OfficeInventory } from "@/types/inventory";

export default function OfficeInventoryPage() {
  const [rows, setRows] = useState<OfficeInventory[]>([]);
  const [message, setMessage] = useState<string>("Loading office inventory...");

  useEffect(() => {
    if (!getStoredToken()) {
      setMessage("No session token found. Sign in first to load live office inventory.");
      return;
    }

    apiFetch("/inventory/office")
      .then((response: OfficeInventory[]) => {
        setRows(response);
        setMessage(response.length ? "Live office inventory loaded from the backend." : "No office inventory rows returned yet.");
      })
      .catch((error: unknown) => {
        setMessage(error instanceof Error ? error.message : "Unable to load office inventory");
      });
  }, []);

  return (
    <AppShell eyebrow="Inventory" title="Office inventory" subtitle="What is physically in the office right now.">
      <InfoCard title="Current office state" description={message}>
        <div className="space-y-3">
          {rows.length ? (
            rows.map((row) => (
              <div key={row.id} className="flex items-center justify-between rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-4 text-sm">
                <div>
                  <p className="font-medium text-white">{row.device_id}</p>
                  <p className="text-[#9f968b]">{row.current_location ?? "No location recorded"}</p>
                </div>
                <span className="rounded-full border border-[#d9ff3f]/35 bg-[#d9ff3f]/10 px-3 py-1 text-xs uppercase tracking-[0.18em] text-[#d9ff3f]">
                  {row.current_status}
                </span>
              </div>
            ))
          ) : (
            <div className="px-4 py-8 text-sm text-[#9f968b]">{message}</div>
          )}
        </div>
      </InfoCard>
    </AppShell>
  );
}
