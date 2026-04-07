"""
Key detection using music21's Krumhansl-Schmuckler algorithm.
"""
from typing import Optional
from music21 import stream, note, analysis

from backend.models.tab import ParsedChord


def detect(chords: list[ParsedChord]) -> tuple[str, str, float]:
    """
    Detect the key from a list of ParsedChords.
    Returns (key_name, mode, confidence) e.g. ("G", "major", 0.92)
    """
    if not chords:
        return ("C", "major", 0.0)

    # Build a music21 stream from all midi pitches
    s = stream.Stream()
    for chord in chords:
        for n in chord.notes:
            if n.midi_pitch is not None:
                s.append(note.Note(midi=n.midi_pitch))

    if len(s.flatten().notes) == 0:
        return ("C", "major", 0.0)

    try:
        k = s.analyze("key")
        confidence = float(k.correlationCoefficient) if hasattr(k, "correlationCoefficient") else 0.7
        return (str(k.tonic.name), str(k.mode), round(confidence, 3))
    except Exception:
        return _fallback_key(chords)


def _fallback_key(chords: list[ParsedChord]) -> tuple[str, str, float]:
    """
    Simple pitch-class counting fallback. Returns the most frequent pitch class
    as tonic with low confidence.
    """
    pitch_class_count: dict[int, int] = {}
    for chord in chords:
        for n in chord.notes:
            if n.midi_pitch is not None:
                pc = n.midi_pitch % 12
                pitch_class_count[pc] = pitch_class_count.get(pc, 0) + 1

    if not pitch_class_count:
        return ("C", "major", 0.0)

    top_pc = max(pitch_class_count, key=lambda k: pitch_class_count[k])
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return (note_names[top_pc], "major", 0.4)
