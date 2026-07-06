"use client";

import { useEffect, useMemo, useState } from "react";
import { RefreshCw } from "lucide-react";

import { AppShell, InfoCard, MetricCard } from "@/components/app-shell";
import { apiFetch } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-store";

type SettingsView = Record<string, string | number | boolean | null>;

function valueText(value: string | number | boolean | null | undefined) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  return String(value);
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsView | null>(null);
  const [message, setMessage] = useState("Loading runtime settings...");
  const [loading, setLoading] = useState(false);

  const groups = useMemo(
    () => [
      {
        title: "Application",
        keys: ["app_env", "frontend_url", "backend_url", "seed_sample_data"],
      },
      {
        title: "Email import",
        keys: [
          "email_import_enabled",
          "email_provider",
          "email_host",
          "email_port",
          "email_tls_verify",
          "email_mailbox",
          "email_search_limit",
          "email_import_interval_hours",
          "email_username",
          "email_app_password_configured",
          "servicenow_email_from",
          "servicenow_email_subject_contains",
        ],
      },
      {
        title: "Intune and scanner",
        keys: ["intune_graph_url", "intune_page_size", "ocr_engine", "yolo_enabled"],
      },
    ],
    [],
  );

  async function loadSettings() {
    if (!getStoredToken()) {
      setMessage("Sign in first to load settings.");
      return;
    }

    setLoading(true);
    try {
      const response = (await apiFetch("/settings")) as SettingsView;
      setSettings(response);
      setMessage("Runtime settings loaded.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load settings");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadSettings();
  }, []);

  return (
    <AppShell eyebrow="Configuration" title="Settings" subtitle={message}>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Environment" value={valueText(settings?.app_env)} tone="accent" detail="Current backend APP_ENV." />
        <MetricCard label="Email import" value={valueText(settings?.email_import_enabled)} tone="neutral" detail={valueText(settings?.email_host)} />
        <MetricCard label="App password" value={valueText(settings?.email_app_password_configured)} tone="alert" detail={valueText(settings?.email_username)} />
        <MetricCard label="YOLO" value={valueText(settings?.yolo_enabled)} tone="neutral" detail={valueText(settings?.ocr_engine)} />
      </div>

      <div className="mt-6">
        <InfoCard title="Runtime values" description="Values come from backend environment variables.">
          <div className="mb-4 flex justify-end">
            <button className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#171716] px-4 py-2 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45" onClick={() => void loadSettings()} type="button">
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
          <div className="grid gap-5 xl:grid-cols-3">
            {groups.map((group) => (
              <section className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4" key={group.title}>
                <h2 className="text-base font-semibold text-white">{group.title}</h2>
                <div className="mt-4 space-y-3 text-sm">
                  {group.keys.map((key) => (
                    <div className="flex items-start justify-between gap-4 border-b border-white/10 pb-2 last:border-b-0 last:pb-0" key={key}>
                      <span className="text-[#9f968b]">{key}</span>
                      <span className="max-w-[60%] break-words text-right text-[#f7f0e7]">{valueText(settings?.[key])}</span>
                    </div>
                  ))}
                </div>
              </section>
            ))}
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
