"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { AppShell, InfoCard } from "@/components/app-shell";
import { getLoginHint } from "@/lib/auth";
import { apiLogin } from "@/lib/api-client";
import { setStoredToken } from "@/lib/auth-store";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("ChangeMe123!");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const token = await apiLogin(email, password);
      setStoredToken(token.access_token);
      setMessage("Signed in. Redirecting to the dashboard.");
      router.push("/dashboard");
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell eyebrow="Access" title="Sign in" subtitle="Authentication shell for the internal inventory system.">
      <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <InfoCard title="Login form" description="Use the seeded admin account for local development.">
          <form className="space-y-4" onSubmit={handleSubmit}>
            <label className="block">
              <span className="mb-2 block text-sm text-[#bdb4a8]">Email</span>
              <input className="w-full rounded-full border border-white/10 bg-[#171716] px-4 py-3 text-white outline-none ring-0 placeholder:text-[#6f675e] focus:border-[#d9ff3f]/60" value={email} onChange={(event) => setEmail(event.target.value)} />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm text-[#bdb4a8]">Password</span>
              <input type="password" className="w-full rounded-full border border-white/10 bg-[#171716] px-4 py-3 text-white outline-none ring-0 placeholder:text-[#6f675e] focus:border-[#d9ff3f]/60" value={password} onChange={(event) => setPassword(event.target.value)} />
            </label>
            <button className="rounded-full bg-[#d9ff3f] px-5 py-3 font-semibold text-[#151512] transition hover:bg-[#efff7a] disabled:cursor-not-allowed disabled:opacity-60" type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Open inventory console"}
            </button>
            {message ? <p className="rounded-[1.15rem] border border-white/10 bg-[#171716] p-4 text-sm text-[#bdb4a8]">{message}</p> : null}
          </form>
        </InfoCard>

        <InfoCard title="Authentication" description="The browser stores the access token for API calls in this session.">
          <div className="space-y-3 text-sm leading-6 text-[#bdb4a8]">
            <p>{getLoginHint()}</p>
            <p>The backend seeds the default admin account on startup using the values in <span className="text-white">.env.example</span>.</p>
            <p>Use the sign out or clear-token control from the dashboard to reset the browser session.</p>
          </div>
        </InfoCard>
      </div>
    </AppShell>
  );
}
