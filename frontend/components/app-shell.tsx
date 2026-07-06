import Link from "next/link";
import { ReactNode } from "react";
import {
  BadgeCheck,
  ArrowUpRight,
  Boxes,
  Camera,
  ChartColumnBig,
  ClipboardList,
  Home,
  Settings2,
  ShieldAlert,
  SlidersHorizontal,
  TabletSmartphone,
  Upload,
  Wifi,
} from "lucide-react";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/dashboard", label: "Dashboard", icon: ChartColumnBig },
  { href: "/devices", label: "Devices", icon: TabletSmartphone },
  { href: "/inventory/office", label: "Office", icon: ClipboardList },
  { href: "/imports/servicenow", label: "ServiceNow", icon: Upload },
  { href: "/sync/intune", label: "Intune", icon: Wifi },
  { href: "/scan", label: "Scan", icon: Camera },
  { href: "/conflicts", label: "Conflicts", icon: ShieldAlert },
  { href: "/reports", label: "Reports", icon: Boxes },
  { href: "/settings", label: "Settings", icon: Settings2 },
];

interface AppShellProps {
  title: string;
  eyebrow?: string;
  subtitle?: string;
  children: ReactNode;
}

export function AppShell({ title, eyebrow, subtitle, children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#d5b18f] p-3 text-[#f8f0e7] md:p-5">
      <div className="mx-auto min-h-[calc(100vh-2.5rem)] max-w-[1880px] overflow-hidden rounded-[2rem] border-[7px] border-[#12110f] bg-[#171716] shadow-[0_28px_80px_rgba(42,24,10,0.35)]">
        <header className="relative min-h-[355px] overflow-hidden border-b border-black/50 bg-[#b89470]">
          <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(110,73,42,0.66),rgba(167,135,101,0.22)_38%,rgba(45,36,28,0.58)_100%)]" />
          <div className="absolute inset-x-[7%] bottom-[-72px] h-56 rounded-[45%] bg-[repeating-linear-gradient(90deg,#8c8171_0,#8c8171_11px,#4f4a41_12px,#4f4a41_17px,#a99f8e_18px,#a99f8e_30px)] opacity-80 shadow-[0_20px_40px_rgba(0,0,0,0.45)]" />
          <div className="absolute left-8 top-20 h-44 w-44 rotate-[-18deg] rounded-lg bg-[#c6945e] opacity-70 shadow-[0_18px_30px_rgba(73,45,23,0.35)]" />
          <div className="absolute right-12 top-0 h-44 w-28 bg-[#9b6b3d] opacity-55 shadow-[0_18px_26px_rgba(45,28,13,0.35)]" />

          <div className="relative z-10 flex flex-wrap items-start justify-between gap-4 px-6 py-5 md:px-8">
            <Link href="/dashboard" className="flex items-center gap-2 text-sm font-semibold text-white">
              <span className="grid h-8 w-8 place-items-center rounded-full border border-white/40 bg-white/15">
                <BadgeCheck className="h-4 w-4" />
              </span>
              Edson IT
            </Link>

            <nav className="flex max-w-4xl flex-wrap justify-center gap-1 rounded-full border border-white/10 bg-[#5e4d3e]/55 p-1 text-xs font-semibold text-white/80 backdrop-blur-md">
              {navItems.map((item, index) => {
                const Icon = item.icon;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "inline-flex h-9 items-center gap-2 rounded-full px-4 transition hover:bg-white/15 hover:text-white",
                      index === 0 ? "bg-white text-[#171716] shadow-[0_6px_18px_rgba(0,0,0,0.18)]" : "",
                    )}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            <div className="flex items-center gap-2">
              <span className="grid h-10 w-10 place-items-center rounded-full border border-white/15 bg-white/15 text-[#dfff3f] backdrop-blur-md">
                <SlidersHorizontal className="h-4 w-4" />
              </span>
              <span className="grid h-10 w-10 place-items-center rounded-full border border-white/15 bg-[#2d261f]/60 text-white backdrop-blur-md">IT</span>
            </div>
          </div>

          <div className="relative z-10 grid gap-6 px-8 pb-8 pt-10 lg:grid-cols-[1fr_0.72fr]">
            <div className="max-w-3xl">
              {eyebrow ? (
                <div className="mb-4 inline-flex items-center gap-3 rounded-full border border-white/45 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white backdrop-blur-md">
                  {eyebrow}
                  <span className="rounded-full border border-white/35 px-3 py-1 text-[10px] tracking-normal">Inventory OS</span>
                </div>
              ) : null}
              <h1 className="max-w-4xl text-5xl font-semibold leading-[0.96] text-white md:text-7xl" style={{ fontFamily: "var(--font-space)" }}>
                {title}
              </h1>
              {subtitle ? <p className="mt-5 max-w-2xl text-base font-medium leading-7 text-white/78">{subtitle}</p> : null}
            </div>

            <div className="self-end rounded-[1.6rem] border border-white/14 bg-[#2a2119]/48 p-5 shadow-[0_20px_50px_rgba(0,0,0,0.24)] backdrop-blur-md">
              <p className="text-sm font-semibold text-white">Inventory movement</p>
              <div className="mt-5 grid grid-cols-3 gap-5">
                {[
                  ["ServiceNow", "Live"],
                  ["Intune", "Ready"],
                  ["Scanner", "Queue"],
                ].map(([label, value]) => (
                  <div key={label}>
                    <p className="text-[11px] font-medium text-white/55">{label}</p>
                    <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
                  </div>
                ))}
              </div>
              <div className="mt-5 h-8 overflow-hidden rounded-full bg-white">
                <div className="h-full w-[72%] rounded-full bg-[#d9ff3f]" />
              </div>
            </div>
          </div>
        </header>

        <main className="bg-[#171716] px-4 py-5 md:px-6 md:py-6">{children}</main>
      </div>
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
  tone?: "accent" | "alert" | "neutral";
  detail?: string;
}

export function MetricCard({ label, value, tone = "neutral", detail }: MetricCardProps) {
  const toneClass =
    tone === "accent"
      ? "border-[#d9ff3f]/35"
      : tone === "alert"
        ? "border-[#caa57f]/45"
        : "border-white/10";

  return (
    <div className={cn("rounded-[1.35rem] border bg-[#23221f] p-5 shadow-[0_18px_38px_rgba(0,0,0,0.24)]", toneClass)}>
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[#bcb3a7]">{label}</p>
        <span className="h-2 w-2 rounded-full bg-[#d9ff3f]" />
      </div>
      <div className="mt-5 text-4xl font-semibold text-white">{value}</div>
      {detail ? <p className="mt-3 text-sm leading-6 text-[#a9a197]">{detail}</p> : null}
    </div>
  );
}

interface InfoCardProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export function InfoCard({ title, description, children }: InfoCardProps) {
  return (
    <section className="rounded-[1.35rem] border border-white/10 bg-[#23221f] p-5 shadow-[0_18px_38px_rgba(0,0,0,0.24)]">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          {description ? <p className="mt-1 text-sm leading-6 text-[#9f968b]">{description}</p> : null}
        </div>
        <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-[#171716] text-[#d9ff3f]">
          <ArrowUpRight className="h-4 w-4" />
        </span>
      </div>
      {children}
    </section>
  );
}
