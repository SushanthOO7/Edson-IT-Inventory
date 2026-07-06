"use client";

import { useEffect, useState } from "react";

import { AppShell, InfoCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";
import type { ConflictRead } from "@/types/conflict";

export default function ConflictsPage() {
  const [conflicts, setConflicts] = useState<ConflictRead[]>([]);
  const [message, setMessage] = useState<string>("Loading conflicts...");

  useEffect(() => {
    if (!getStoredToken()) {
      setMessage("No session token found. Sign in first to load live conflicts.");
      return;
    }

    apiFetch("/conflicts")
      .then((response: ConflictRead[]) => {
        setConflicts(response);
        setMessage(response.length ? "Live conflicts loaded from the backend." : "No conflicts returned yet.");
      })
      .catch((error: unknown) => {
        setMessage(error instanceof Error ? error.message : "Unable to load conflicts");
      });
  }, []);

  return (
    <AppShell eyebrow="Review" title="Conflicts" subtitle="Surface every mismatch and let the operator decide which truth to keep.">
      <InfoCard title="Open conflicts" description={message}>
        <div className="space-y-3">
          {conflicts.length ? (
            conflicts.map((conflict) => (
              <div key={conflict.id} className="grid gap-3 rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-4 text-sm md:grid-cols-[0.8fr_1fr_1fr_auto]">
                <div className="font-medium text-white">{conflict.field_name}</div>
                <div className="text-[#bdb4a8]">Local: {conflict.local_value ?? "None"}</div>
                <div className="text-[#bdb4a8]">External: {conflict.service_now_value ?? conflict.intune_value ?? conflict.ocr_value ?? "None"}</div>
                <div className="text-[#f0d0ad]">{conflict.status}</div>
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
