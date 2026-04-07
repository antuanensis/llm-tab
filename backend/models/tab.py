from pydantic import BaseModel
from typing import Literal, Optional


class TabInput(BaseModel):
    tab_text: str
    tuning: str = "standard"  # standard, drop_d, open_g, etc.
    capo: int = 0
    provider: Optional[Literal["anthropic", "ollama", "openai"]] = None


class ParsedNote(BaseModel):
    string_name: str   # e, B, G, D, A, E (low)
    string_index: int  # 0=high-e, 5=low-E
    fret: Optional[int]  # None = muted
    midi_pitch: Optional[int]


class ParsedChord(BaseModel):
    position: int  # column index in the tab
    notes: list[ParsedNote]
    raw_label: Optional[str] = None  # e.g. "G" if annotated in the tab
