"use client";

import { useEffect, useState } from "react";
import { Check, RefreshCw, X } from "lucide-react";

import { AppShell, InfoCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";
import type { ConflictRead } from "@/types/conflict";

export default function ConflictsPage() {
  const [conflicts, setConflicts] = useState<ConflictRead[]>([]);
  const [message, setMessage] = useState<string>("Loading conflicts...");
  const [actingId, setActingId] = useState<string | null>(null);

  async function loadConflicts() {
    if (!getStoredToken()) {
      setMessage("No session token found. Sign in first to load live conflicts.");
      return;
    }

    try {
      const response = (await apiFetch("/conflicts")) as ConflictRead[];
      setConflicts(response);
      setMessage(response.length ? `${response.length} conflicts loaded from the backend.` : "No conflicts returned yet.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load conflicts");
    }
  }

  useEffect(() => {
    void loadConflicts();
  }, []);

  async function resolveConflict(conflict: ConflictRead, resolvedValue: string | null) {
    setActingId(conflict.id);
    try {
      await apiFetch(`/conflicts/${conflict.id}/resolve`, {
        method: "POST",
        body: JSON.stringify({
          resolved_value: resolvedValue,
          status: "RESOLVED",
        }),
      });
      await loadConflicts();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to resolve conflict");
    } finally {
      setActingId(null);
    }
  }

  async function ignoreConflict(conflict: ConflictRead) {
    setActingId(conflict.id);
    try {
      await apiFetch(`/conflicts/${conflict.id}/ignore`, { method: "POST" });
      await loadConflicts();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to ignore conflict");
    } finally {
      setActingId(null);
    }
  }

  return (
    <AppShell eyebrow="Review" title="Conflicts" subtitle="Surface every mismatch and let the operator decide which truth to keep.">
      <InfoCard title="Open conflicts" description={message}>
        <div className="mb-4 flex justify-end">
          <button className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#171716] px-4 py-2 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45" onClick={() => void loadConflicts()} type="button">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
        <div className="space-y-3">
          {conflicts.length ? (
            conflicts.map((conflict) => (
              <div key={conflict.id} className="grid gap-3 rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-4 text-sm xl:grid-cols-[0.75fr_1fr_1fr_0.7fr_auto]">
                <div className="font-medium text-white">{conflict.field_name}</div>
                <div className="text-[#bdb4a8]">Local: {conflict.local_value ?? "None"}</div>
                <div className="text-[#bdb4a8]">External: {conflict.service_now_value ?? conflict.intune_value ?? conflict.ocr_value ?? "None"}</div>
                <div className="text-[#f0d0ad]">{conflict.status}</div>
                <div className="flex flex-wrap gap-2">
                  <button
                    className="inline-flex items-center gap-1 rounded-full bg-[#d9ff3f] px-3 py-1.5 text-xs font-semibold text-[#151512] disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={actingId === conflict.id || conflict.status !== "OPEN"}
                    onClick={() => void resolveConflict(conflict, conflict.local_value ?? null)}
                    type="button"
                  >
                    <Check className="h-3.5 w-3.5" />
                    Local
                  </button>
                  <button
                    className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-[#23221f] px-3 py-1.5 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={actingId === conflict.id || conflict.status !== "OPEN"}
                    onClick={() => void resolveConflict(conflict, conflict.service_now_value ?? conflict.intune_value ?? conflict.ocr_value ?? null)}
                    type="button"
                  >
                    <Check className="h-3.5 w-3.5" />
                    External
                  </button>
                  <button
                    className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-[#23221f] px-3 py-1.5 text-xs font-semibold text-[#f0d0ad] disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={actingId === conflict.id || conflict.status !== "OPEN"}
                    onClick={() => void ignoreConflict(conflict)}
                    type="button"
                  >
                    <X className="h-3.5 w-3.5" />
                    Ignore
                  </button>
                </div>
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
