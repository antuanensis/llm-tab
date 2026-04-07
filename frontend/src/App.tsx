import { useState } from "react";
import { analyzeTab } from "./api/analyzeTab";
import { TabInput } from "./components/TabInput";
import { EnrichedOutput } from "./components/EnrichedOutput";
import { LoadingSpinner } from "./components/LoadingSpinner";
import type { EnrichedOutput as EnrichedOutputType } from "./types/analysis";

export function App() {
  const [tabText, setTabText] = useState("");
  const [provider, setProvider] = useState<string>("ollama");
  const [result, setResult] = useState<EnrichedOutputType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeTab(tabText, "standard", 0, provider);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>llm-tab</h1>
        <p className="tagline">Paste any guitar tab. Get a music theory lesson.</p>
      </header>
      <main className="app-main">
        <TabInput
          value={tabText}
          onChange={setTabText}
          onSubmit={handleSubmit}
          loading={loading}
          provider={provider}
          onProviderChange={setProvider}
        />
        {loading && <LoadingSpinner provider={provider} />}
        {error && <div className="error-box">{error}</div>}
        {result && <EnrichedOutput data={result} />}
      </main>
    </div>
  );
}
