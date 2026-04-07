import type { EnrichedOutput } from "../types/analysis";

export async function analyzeTab(tabText: string, tuning = "standard", capo = 0, provider?: string): Promise<EnrichedOutput> {
  const response = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tab_text: tabText, tuning, capo, provider: provider ?? null }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail ?? `HTTP ${response.status}`);
  }

  return response.json() as Promise<EnrichedOutput>;
}
