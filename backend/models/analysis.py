from pydantic import BaseModel
from typing import Optional


class ScaleSuggestion(BaseModel):
    name: str          # e.g. "G Major (Ionian)"
    notes: list[str]   # e.g. ["G", "A", "B", "C", "D", "E", "F#"]
    use_case: str      # e.g. "Primary diatonic choice"


class ChordAnalysis(BaseModel):
    position: int
    chord_name: str         # e.g. "G major"
    root: str               # e.g. "G"
    quality: str            # e.g. "major", "minor", "dominant7"
    roman_numeral: str      # e.g. "I", "IV", "V", "vi"
    is_diatonic: bool
    non_diatonic_type: Optional[str] = None  # "borrowed", "secondary_dominant", etc.
    scales: list[ScaleSuggestion]
    guide_tones: list[str]  # e.g. ["G", "B", "D"]


class TheoryAnalysis(BaseModel):
    key: str                    # e.g. "G major"
    mode: str                   # e.g. "major", "minor"
    key_confidence: float       # 0.0 – 1.0
    chords: list[ChordAnalysis]
    progression_numerals: list[str]  # e.g. ["I", "IV", "V", "vi"]
    has_borrowed_chords: bool
    has_secondary_dominants: bool
    has_modulation: bool
