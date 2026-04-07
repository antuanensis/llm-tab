export interface ScaleSuggestion {
  name: string;
  notes: string[];
  use_case: string;
}

export interface ChordAnalysis {
  position: number;
  chord_name: string;
  root: string;
  quality: string;
  roman_numeral: string;
  is_diatonic: boolean;
  non_diatonic_type: string | null;
  scales: ScaleSuggestion[];
  guide_tones: string[];
}

export interface TheoryAnalysis {
  key: string;
  mode: string;
  key_confidence: number;
  chords: ChordAnalysis[];
  progression_numerals: string[];
  has_borrowed_chords: boolean;
  has_secondary_dominants: boolean;
  has_modulation: boolean;
}

export interface PracticeExercise {
  number: number;
  description: string;
}

export interface EnrichedOutput {
  theory: TheoryAnalysis;
  beginner_summary: string;
  theory_deep_dive: string;
  scale_suggestions_narrative: string;
  guide_tones_narrative: string;
  practice_exercises: PracticeExercise[];
  cheat_sheet: string;
  input_tab: string;
  confidence_label: "high" | "medium" | "low";
}
