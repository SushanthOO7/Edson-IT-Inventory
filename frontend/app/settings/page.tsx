import { AppShell, InfoCard } from "@/components/app-shell";

export default function SettingsPage() {
  return (
    <AppShell eyebrow="Configuration" title="Settings" subtitle="Keep credentials, endpoints, and feature flags outside the source tree.">
      <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <InfoCard title="Runtime settings" description="These values are backed by environment variables in the backend.">
          <div className="space-y-3 text-sm leading-6 text-[#bdb4a8]">
            <p>ServiceNow required columns.</p>
            <p>Graph URL and page size.</p>
            <p>Email import settings.</p>
            <p>OCR and YOLO feature flags.</p>
          </div>
        </InfoCard>
        <InfoCard title="Recommended guardrails" description="Keep the app on a private network and restrict mutating actions to admins.">
          <div className="space-y-3 text-sm leading-6 text-[#bdb4a8]">
            <p>Do not store the Intune token.</p>
            <p>Do not expose PostgreSQL or Redis publicly.</p>
            <p>Use backups before big imports.</p>
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
