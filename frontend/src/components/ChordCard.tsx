import type { ChordAnalysis } from "../types/analysis";

interface Props {
  chord: ChordAnalysis;
}

export function ChordCard({ chord }: Props) {
  return (
    <div className={`chord-card ${chord.is_diatonic ? "" : "non-diatonic"}`}>
      <div className="chord-header">
        <span className="chord-name">{chord.chord_name}</span>
        <span className="chord-numeral">{chord.roman_numeral}</span>
        {chord.non_diatonic_type && (
          <span className="badge non-diatonic-badge">{chord.non_diatonic_type}</span>
        )}
      </div>
      <div className="chord-detail">
        <span className="label">Guide tones:</span> {chord.guide_tones.join(", ")}
      </div>
      <div className="chord-scales">
        {chord.scales.map((s) => (
          <div key={s.name} className="scale-item">
            <strong>{s.name}</strong> — {s.use_case}
            <span className="scale-notes">{s.notes.join(" · ")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
