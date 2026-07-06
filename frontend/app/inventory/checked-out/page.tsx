import { AppShell, InfoCard } from "@/components/app-shell";

export default function CheckedOutPage() {
  return (
    <AppShell eyebrow="Inventory" title="Checked out" subtitle="Devices that have left the IT office and need return tracking.">
      <InfoCard title="Loaned devices" description="Return dates, users, and handoff notes belong here.">
        <div className="rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-8 text-sm text-[#9f968b]">No checked-out devices loaded.</div>
      </InfoCard>
    </AppShell>
  );
}
