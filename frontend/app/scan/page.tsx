import { AppShell, InfoCard } from "@/components/app-shell";

export default function ScanPage() {
  return (
    <AppShell eyebrow="Scanner" title="Webcam OCR" subtitle="Capture a frame, extract the asset tag, and present the best matching devices for confirmation.">
      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <InfoCard title="Capture surface" description="The backend pipeline starts with OCR and can later add YOLO-based label detection.">
          <div className="rounded-[1.35rem] border border-dashed border-[#d9ff3f]/35 bg-[#171716] p-8 text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#9f968b]">Live camera preview</p>
            <div className="mt-4 grid h-64 place-items-center rounded-[1.15rem] bg-[linear-gradient(135deg,#2b2924,#181817)] text-[#bdb4a8]">
              Camera feed placeholder
            </div>
          </div>
        </InfoCard>
        <InfoCard title="Expected behavior" description="The user confirms the match before the inventory record changes.">
          <div className="space-y-3 text-sm leading-6 text-[#bdb4a8]">
            <p>OCR reads asset tags from device labels.</p>
            <p>The matching engine scores candidate devices.</p>
            <p>Low-confidence scans stay pending review.</p>
            <p>Confirm, check out, check in, or move to repair from the scan result.</p>
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
