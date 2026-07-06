import { AppShell, InfoCard } from "@/components/app-shell";

const reports = [
  "Dashboard summary",
  "Office inventory",
  "Checked out",
  "Overdue loaners",
  "Missing devices",
  "ServiceNow not Intune",
  "Intune not ServiceNow",
  "Open conflicts",
];

export default function ReportsPage() {
  return (
    <AppShell eyebrow="Reporting" title="Reports" subtitle="Curated views and exports for the team's daily inventory tasks.">
      <InfoCard title="Available reports" description="The backend is wired for report endpoints and CSV export.">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {reports.map((report) => (
            <div key={report} className="rounded-[1.15rem] border border-white/10 bg-[#171716] px-4 py-4 text-sm text-[#d8d0c5]">
              {report}
            </div>
          ))}
        </div>
      </InfoCard>
    </AppShell>
  );
}
