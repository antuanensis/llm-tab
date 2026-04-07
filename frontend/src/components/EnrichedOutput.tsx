import type { EnrichedOutput as EnrichedOutputType } from "../types/analysis";
import { ChordCard } from "./ChordCard";
import { PracticeExercises } from "./PracticeExercises";
import { CheatSheet } from "./CheatSheet";

interface Props {
  data: EnrichedOutputType;
}

const CONFIDENCE_COLORS: Record<string, string> = {
  high: "#2ecc71",
  medium: "#f39c12",
  low: "#e74c3c",
};

export function EnrichedOutput({ data }: Props) {
  const { theory } = data;

  return (
    <div className="enriched-output">
      <header className="output-header">
        <h2>
          Key: {theory.key} {theory.mode}
        </h2>
        <span
          className="confidence-badge"
          style={{ background: CONFIDENCE_COLORS[data.confidence_label] }}
        >
          {data.confidence_label} confidence
        </span>
        <div className="progression-numerals">
          {theory.progression_numerals.join(" → ")}
        </div>
      </header>

      <section className="section">
        <h3>Quick Summary</h3>
        <p>{data.beginner_summary}</p>
      </section>

      <section className="section">
        <h3>Theory Deep Dive</h3>
        <p>{data.theory_deep_dive}</p>
      </section>

      <section className="section">
        <h3>Chord Breakdown</h3>
        <div className="chord-grid">
          {theory.chords.map((chord) => (
            <ChordCard key={`${chord.position}-${chord.chord_name}`} chord={chord} />
          ))}
        </div>
      </section>

      <section className="section">
        <h3>Scale & Improv Guide</h3>
        <p>{data.scale_suggestions_narrative}</p>
        <p>{data.guide_tones_narrative}</p>
      </section>

      <PracticeExercises exercises={data.practice_exercises} />
      <CheatSheet text={data.cheat_sheet} />
    </div>
  );
}
