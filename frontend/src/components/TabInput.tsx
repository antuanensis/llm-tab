interface Props {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  loading: boolean;
  provider: string;
  onProviderChange: (v: string) => void;
}

const PLACEHOLDER = `Paste your ASCII tab here, e.g.:

e|---3---0---2---0---
B|---0---1---3---0---
G|---0---0---2---0---
D|---0---2---0---2---
A|---2---3---x---2---
E|---3---x---x---0---
  G   C   D  Em`;

const PROVIDERS = [
  { value: "ollama", label: "Ollama (local)" },
  { value: "anthropic", label: "Claude (Anthropic)" },
  { value: "openai", label: "OpenAI / OpenRouter" },
];

export function TabInput({ value, onChange, onSubmit, loading, provider, onProviderChange }: Props) {
  return (
    <div className="tab-input-panel">
      <h2>Paste Your Tab</h2>
      <textarea
        className="tab-textarea"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={PLACEHOLDER}
        rows={12}
        spellCheck={false}
      />
      <div className="tab-controls">
        <select
          className="provider-select"
          value={provider}
          onChange={(e) => onProviderChange(e.target.value)}
          disabled={loading}
        >
          {PROVIDERS.map((p) => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
        <button className="analyze-btn" onClick={onSubmit} disabled={loading || !value.trim()}>
          {loading ? "Analyzing..." : "Analyze Tab"}
        </button>
      </div>
    </div>
  );
}
