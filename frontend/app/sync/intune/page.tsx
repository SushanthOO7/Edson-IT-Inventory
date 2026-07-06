import { AppShell, InfoCard } from "@/components/app-shell";

export default function IntuneSyncPage() {
  return (
    <AppShell eyebrow="Sync" title="Intune sync" subtitle="Paste the bearer token, fetch the managed devices, and discard the token immediately after use.">
      <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <InfoCard title="Sync flow" description="The backend should page through all Graph results and then compare them with the device master list.">
          <div className="space-y-3 text-sm leading-6 text-[#bdb4a8]">
            <p>1. Admin pastes a Graph bearer token.</p>
            <p>2. Backend fetches Intune records through the configured Graph URL.</p>
            <p>3. Pagination continues until the final page is reached.</p>
            <p>4. Results are stored as a raw JSON snapshot and matched to devices.</p>
          </div>
        </InfoCard>
        <InfoCard title="Security reminders" description="The token is never persisted, logged, or echoed back to the browser.">
          <div className="space-y-3 text-sm leading-6 text-[#bdb4a8]">
            <p>Keep the page restricted to admin users.</p>
            <p>Use HTTPS if this ever moves beyond a local team environment.</p>
            <p>Prefer Entra app registration later if the organization approves it.</p>
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
