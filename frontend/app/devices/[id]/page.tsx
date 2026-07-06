"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { AppShell, InfoCard, MetricCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";
import type { ConflictRead } from "@/types/conflict";
import type { Device } from "@/types/device";
import type { InventoryEvent, OfficeInventory } from "@/types/inventory";

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function valueOrDash(value?: string | number | null) {
  return value === null || value === undefined || value === "" ? "-" : String(value);
}

export default function DeviceDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [device, setDevice] = useState<Device | null>(null);
  const [officeRow, setOfficeRow] = useState<OfficeInventory | null>(null);
  const [events, setEvents] = useState<InventoryEvent[]>([]);
  const [conflicts, setConflicts] = useState<ConflictRead[]>([]);
  const [message, setMessage] = useState("Loading device detail...");

  useEffect(() => {
    if (!getStoredToken()) {
      setMessage("Sign in first to load device details.");
      return;
    }

    async function loadDevice() {
      try {
        const [deviceResponse, historyResponse, conflictResponse, officeResponse] = await Promise.all([
          apiFetch(`/devices/${id}`),
          apiFetch(`/devices/${id}/history`),
          apiFetch(`/devices/${id}/conflicts`),
          apiFetch("/inventory/office"),
        ]);
        setDevice(deviceResponse as Device);
        setEvents(historyResponse as InventoryEvent[]);
        setConflicts(conflictResponse as ConflictRead[]);
        setOfficeRow((officeResponse as OfficeInventory[]).find((row) => row.device_id === id) ?? null);
        setMessage("Device detail loaded.");
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Unable to load device detail");
      }
    }

    void loadDevice();
  }, [id]);

  const title = useMemo(() => {
    if (!device) {
      return `Device ${id}`;
    }
    return device.asset_tag ?? device.display_name ?? device.device_name ?? `Device ${id}`;
  }, [device, id]);

  return (
    <AppShell eyebrow="Device detail" title={title} subtitle={message}>
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="Source confidence" value={device ? `${Math.round(device.source_confidence)}%` : "-"} tone="accent" detail={device?.lifecycle_status ?? "No confidence recorded yet."} />
        <MetricCard label="Office status" value={officeRow?.current_status ?? "Untracked"} tone="neutral" detail={officeRow?.current_location ?? "No office location recorded."} />
        <MetricCard label="Open conflicts" value={String(conflicts.filter((conflict) => conflict.status === "OPEN").length)} tone="alert" detail={`${conflicts.length} total conflict records.`} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <InfoCard title="Identity" description="Core fields and cross-system keys.">
          <div className="grid gap-3 text-sm text-[#bdb4a8] sm:grid-cols-2">
            <p>Asset tag: <span className="text-white">{valueOrDash(device?.asset_tag)}</span></p>
            <p>Serial: <span className="text-white">{valueOrDash(device?.serial_number)}</span></p>
            <p>Name: <span className="text-white">{valueOrDash(device?.device_name)}</span></p>
            <p>Display: <span className="text-white">{valueOrDash(device?.display_name)}</span></p>
            <p>Model: <span className="text-white">{valueOrDash(device?.model ?? device?.model_category)}</span></p>
            <p>Type: <span className="text-white">{valueOrDash(device?.device_type)}</span></p>
            <p>MAC: <span className="text-white">{valueOrDash(device?.mac_address)}</span></p>
            <p>Department: <span className="text-white">{valueOrDash(device?.department)}</span></p>
            <p>Cost center: <span className="text-white">{valueOrDash(device?.cost_center)}</span></p>
            <p>Updated: <span className="text-white">{formatDate(device?.updated_at)}</span></p>
          </div>
        </InfoCard>

        <InfoCard title="Office state" description="Current physical inventory record for this device.">
          <div className="grid gap-3 text-sm text-[#bdb4a8] sm:grid-cols-2">
            <p>Status: <span className="text-white">{officeRow?.current_status ?? "Untracked"}</span></p>
            <p>Location: <span className="text-white">{valueOrDash(officeRow?.current_location)}</span></p>
            <p>Assigned: <span className="text-white">{valueOrDash(officeRow?.assigned_user_name ?? officeRow?.checked_out_to)}</span></p>
            <p>Email: <span className="text-white">{valueOrDash(officeRow?.assigned_user_email)}</span></p>
            <p>Checked out: <span className="text-white">{formatDate(officeRow?.checked_out_at)}</span></p>
            <p>Expected return: <span className="text-white">{formatDate(officeRow?.expected_return_at)}</span></p>
            <p>Condition: <span className="text-white">{valueOrDash(officeRow?.condition)}</span></p>
            <p>Notes: <span className="text-white">{valueOrDash(officeRow?.notes)}</span></p>
          </div>
        </InfoCard>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <InfoCard title="Timeline" description={`${events.length} inventory movement records.`}>
          <div className="space-y-3">
            {events.length ? (
              events.map((event) => (
                <div key={event.id} className="rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-4 text-sm">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="font-semibold text-white">{event.event_type}</p>
                    <p className="text-xs text-[#9f968b]">{formatDate(event.created_at)}</p>
                  </div>
                  <p className="mt-2 text-[#bdb4a8]">{valueOrDash(event.from_status)} to {valueOrDash(event.to_status)}</p>
                  <p className="mt-1 text-[#9f968b]">{valueOrDash(event.notes ?? event.location ?? event.performed_by)}</p>
                </div>
              ))
            ) : (
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-8 text-sm text-[#9f968b]">No inventory movement records found.</div>
            )}
          </div>
        </InfoCard>

        <InfoCard title="Conflicts" description={`${conflicts.length} conflict records for this device.`}>
          <div className="space-y-3">
            {conflicts.length ? (
              conflicts.map((conflict) => (
                <div key={conflict.id} className="rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-4 text-sm">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="font-semibold text-white">{conflict.field_name}</p>
                    <span className="rounded-full border border-[#d9ff3f]/35 px-3 py-1 text-xs uppercase tracking-[0.18em] text-[#d9ff3f]">{conflict.status}</span>
                  </div>
                  <p className="mt-2 text-[#bdb4a8]">Local: <span className="text-white">{valueOrDash(conflict.local_value)}</span></p>
                  <p className="mt-1 text-[#bdb4a8]">External: <span className="text-white">{valueOrDash(conflict.service_now_value ?? conflict.intune_value ?? conflict.ocr_value)}</span></p>
                </div>
              ))
            ) : (
              <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-8 text-sm text-[#9f968b]">No conflicts found for this device.</div>
            )}
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
