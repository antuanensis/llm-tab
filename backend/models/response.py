from pydantic import BaseModel
from .analysis import TheoryAnalysis, ChordAnalysis


class PracticeExercise(BaseModel):
    number: int
    description: str


class EnrichedOutput(BaseModel):
    # Theory data (deterministic)
    theory: TheoryAnalysis

    # LLM-generated content
    beginner_summary: str
    theory_deep_dive: str
    scale_suggestions_narrative: str
    guide_tones_narrative: str
    practice_exercises: list[PracticeExercise]
    cheat_sheet: str

    # Metadata
    input_tab: str
    confidence_label: str  # "high", "medium", "low"
