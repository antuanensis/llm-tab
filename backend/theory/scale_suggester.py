"""
Rule-based scale suggestion engine.
Given a chord root, quality, and key context, returns ordered scale suggestions.
"""
from backend.models.analysis import ScaleSuggestion

# Semitone intervals for common scales (relative to root)
_SCALE_INTERVALS: dict[str, list[int]] = {
    "Major (Ionian)":        [0, 2, 4, 5, 7, 9, 11],
    "Natural Minor (Aeolian)": [0, 2, 3, 5, 7, 8, 10],
    "Dorian":                [0, 2, 3, 5, 7, 9, 10],
    "Mixolydian":            [0, 2, 4, 5, 7, 9, 10],
    "Phrygian":              [0, 1, 3, 5, 7, 8, 10],
    "Lydian":                [0, 2, 4, 6, 7, 9, 11],
    "Locrian":               [0, 1, 3, 5, 6, 8, 10],
    "Major Pentatonic":      [0, 2, 4, 7, 9],
    "Minor Pentatonic":      [0, 3, 5, 7, 10],
    "Blues":                 [0, 3, 5, 6, 7, 10],
}

_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _note_from_pc(root: str, semitones: int) -> str:
    try:
        root_pc = _NOTE_NAMES.index(root.replace("b", "").replace("#", ""))
        pc = (root_pc + semitones) % 12
        return _NOTE_NAMES[pc]
    except ValueError:
        return "?"


def _build_scale(root: str, scale_name: str) -> list[str]:
    intervals = _SCALE_INTERVALS[scale_name]
    return [_note_from_pc(root, i) for i in intervals]


def suggest_scales(root: str, quality: str, key_name: str, mode: str) -> list[ScaleSuggestion]:
    suggestions: list[ScaleSuggestion] = []

    if quality in ("major", "dominant", "dominant-seventh"):
        # Primary: diatonic mode
        if root == key_name:
            name = "Major (Ionian)"
            use_case = "Primary diatonic choice — home key"
        else:
            name = "Mixolydian"
            use_case = "Dominant color — slightly bluesy major feel"
        suggestions.append(ScaleSuggestion(
            name=f"{root} {name}",
            notes=_build_scale(root, name),
            use_case=use_case,
        ))
        suggestions.append(ScaleSuggestion(
            name=f"{root} Major Pentatonic",
            notes=_build_scale(root, "Major Pentatonic"),
            use_case="Safe, singable — works over the full progression",
        ))

    elif quality in ("minor", "minor-seventh"):
        suggestions.append(ScaleSuggestion(
            name=f"{root} Natural Minor (Aeolian)",
            notes=_build_scale(root, "Natural Minor (Aeolian)"),
            use_case="Default minor color",
        ))
        suggestions.append(ScaleSuggestion(
            name=f"{root} Dorian",
            notes=_build_scale(root, "Dorian"),
            use_case="Minor with raised 6th — brighter, jazzier",
        ))
        suggestions.append(ScaleSuggestion(
            name=f"{root} Minor Pentatonic",
            notes=_build_scale(root, "Minor Pentatonic"),
            use_case="Easy box shapes, universal minor soloing",
        ))

    elif quality in ("diminished", "half-diminished"):
        suggestions.append(ScaleSuggestion(
            name=f"{root} Locrian",
            notes=_build_scale(root, "Locrian"),
            use_case="Unstable, tense — resolves tension",
        ))

    else:
        # Fallback: suggest key-based pentatonic
        suggestions.append(ScaleSuggestion(
            name=f"{key_name} Major Pentatonic",
            notes=_build_scale(key_name, "Major Pentatonic"),
            use_case="Key-wide safe choice",
        ))

    return suggestions
