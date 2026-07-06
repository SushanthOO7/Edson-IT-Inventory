import { AppShell, InfoCard, MetricCard } from "@/components/app-shell";

type DeviceDetailPageProps = {
  params: Promise<{ id: string }>;
};

export default async function DeviceDetailPage({ params }: DeviceDetailPageProps) {
  const { id } = await params;

  return (
    <AppShell eyebrow="Device detail" title={`Device ${id}`} subtitle="Identity, office status, source records, scan results, and history live on the same page.">
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="Source confidence" value="-" tone="accent" detail="Live detail loading will populate this value." />
        <MetricCard label="Office status" value="-" tone="neutral" detail="Tracked separately from ServiceNow and Intune state." />
        <MetricCard label="Open conflicts" value="-" tone="alert" detail="Review before the next import or sync mutates the record." />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <InfoCard title="Identity" description="Core fields and cross-system keys.">
          <div className="grid gap-3 text-sm text-[#bdb4a8] sm:grid-cols-2">
            <p>Asset tag: <span className="text-white">-</span></p>
            <p>Serial: <span className="text-white">-</span></p>
            <p>Model: <span className="text-white">-</span></p>
            <p>User: <span className="text-white">-</span></p>
            <p>Status: <span className="text-white">-</span></p>
            <p>Department: <span className="text-white">-</span></p>
          </div>
        </InfoCard>
        <InfoCard title="Timeline" description="Every inventory movement should append here.">
          <div className="text-sm text-[#bdb4a8]">No timeline events loaded.</div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
