"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AppShell, InfoCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";
import type { Device } from "@/types/device";

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [message, setMessage] = useState<string>("Loading device list...");

  useEffect(() => {
    if (!getStoredToken()) {
      setMessage("No session token found. Sign in first to load live devices.");
      return;
    }

    apiFetch("/devices?limit=20")
      .then((response: { items: Device[] }) => {
        setDevices(response.items);
        setMessage(response.items.length ? "Live rows loaded from the backend." : "No devices returned from the backend yet.");
      })
      .catch((error: unknown) => {
        setMessage(error instanceof Error ? error.message : "Unable to load device list");
      });
  }, []);

  return (
    <AppShell eyebrow="Inventory" title="Devices" subtitle="Searchable master inventory with the important fields surfaced up front.">
      <InfoCard title="Device list" description={message}>
        <div className="overflow-hidden rounded-[1.15rem] border border-white/10">
          {devices.length ? (
            devices.map((device, index) => (
              <div key={device.id} className={`grid grid-cols-5 gap-4 px-4 py-4 text-sm ${index % 2 === 0 ? "bg-[#171716]" : "bg-[#2a2925]"}`}>
                <Link className="font-medium text-[#d9ff3f] hover:text-[#efff7a]" href={`/devices/${device.id}`}>
                  {device.asset_tag ?? "Unknown"}
                </Link>
                <div className="text-white">{device.display_name ?? device.device_name ?? "Unnamed device"}</div>
                <div className="text-[#bdb4a8]">{device.lifecycle_status}</div>
                <div className="text-[#bdb4a8]">{device.department ?? "Unassigned"}</div>
                <div className="text-right text-[#9f968b]">{device.source_confidence}%</div>
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
