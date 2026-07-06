import Link from "next/link";
import { ArrowRight, Camera, Layers3, ShieldCheck, Upload } from "lucide-react";

import { AppShell, InfoCard, MetricCard } from "@/components/app-shell";

export default function HomePage() {
  return (
    <AppShell eyebrow="IT Inventory" title="Own the inventory outcome" subtitle="A warehouse-style operating view for ServiceNow imports, Intune syncs, office stock, scanner review, and conflict cleanup.">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="ServiceNow" value="Sync" tone="accent" detail="Pull the latest CSV from email and inspect every device row." />
        <MetricCard label="Office stock" value="Live" tone="neutral" detail="Keep local inventory separate from imported system state." />
        <MetricCard label="Conflicts" value="Review" tone="alert" detail="Resolve mismatches without overwriting trusted local records." />
        <MetricCard label="Scanner" value="Ready" tone="neutral" detail="Use OCR-assisted asset tag capture for physical workflows." />
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <InfoCard title="March report" description="Move from seed placeholders to real ServiceNow and office inventory rows.">
          <div className="grid gap-3 md:grid-cols-2">
            {[
              { icon: Upload, title: "Import-safe", text: "CSV snapshots are stored separately, then matched into master devices by exact identifiers." },
              { icon: Layers3, title: "Distribution view", text: "Use search, filters, and pagination to inspect all loaded ServiceNow assets." },
              { icon: Camera, title: "Scanner workflow", text: "Confirm OCR matches before changing inventory records." },
              { icon: ShieldCheck, title: "Conflict-aware", text: "Bad matches become review work instead of silent overwrites." },
            ].map((feature) => (
              <div key={feature.title} className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4">
                <feature.icon className="h-5 w-5 text-[#d9ff3f]" />
                <h2 className="mt-4 text-base font-semibold text-white">{feature.title}</h2>
                <p className="mt-2 text-sm leading-6 text-[#a9a197]">{feature.text}</p>
              </div>
            ))}
          </div>
        </InfoCard>

        <InfoCard title="Start here" description="Open the operational screens instead of a marketing-style landing page.">
          <div className="space-y-3">
            <Link href="/dashboard" className="inline-flex w-full items-center justify-between rounded-full bg-[#d9ff3f] px-5 py-3 text-sm font-semibold text-[#151512] transition hover:bg-[#efff7a]">
              Dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/imports/servicenow" className="inline-flex w-full items-center justify-between rounded-full border border-white/10 bg-[#171716] px-5 py-3 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45">
              ServiceNow sync
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/devices" className="inline-flex w-full items-center justify-between rounded-full border border-white/10 bg-[#171716] px-5 py-3 text-sm font-semibold text-white transition hover:border-[#d9ff3f]/45">
              Device inventory
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
