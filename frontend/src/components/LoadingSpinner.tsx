interface Props {
  provider?: string;
}

const PROVIDER_LABELS: Record<string, string> = {
  anthropic: "Claude",
  ollama: "Ollama (local)",
  openai: "OpenAI",
};

export function LoadingSpinner({ provider }: Props) {
  const label = provider ? (PROVIDER_LABELS[provider] ?? provider) : "AI";
  return (
    <div className="spinner-wrap">
      <div className="spinner" />
      <p>Analyzing your tab with {label}...</p>
    </div>
  );
}
