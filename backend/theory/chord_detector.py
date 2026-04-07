"""
Chord detection: converts sets of MIDI pitches into named chords with Roman numerals.
Uses music21 for chord naming and harmonic analysis.
"""
from music21 import chord as m21chord, key as m21key, roman

from backend.models.tab import ParsedChord
from backend.models.analysis import ChordAnalysis
from backend.theory.scale_suggester import suggest_scales


def _midi_to_chord(midi_pitches: list[int]) -> tuple[str, str, str]:
    """
    Returns (chord_name, root, quality) for a set of MIDI pitches.
    e.g. ([55, 59, 62, 67], ...) -> ("G major", "G", "major")
    """
    if not midi_pitches:
        return ("Unknown", "?", "unknown")

    try:
        c = m21chord.Chord(midi_pitches)
        root = c.root().name
        quality = c.quality  # 'major', 'minor', 'diminished', etc.
        chord_name = f"{root} {quality}"
        return (chord_name, root, quality)
    except Exception:
        return ("Unknown", "?", "unknown")


def _roman_numeral(chord_root: str, chord_quality: str, key_name: str, mode: str) -> tuple[str, bool, str | None]:
    """
    Returns (roman_numeral, is_diatonic, non_diatonic_type).
    """
    try:
        k = m21key.Key(key_name, mode)
        # Build a minimal chord and find its roman numeral
        c = m21chord.Chord([chord_root + "4"])
        rn = roman.romanNumeralFromChord(c, k)
        numeral = rn.figure
        # Determine if diatonic
        scale_pcs = {p.pitchClass for p in k.pitches}
        try:
            from music21 import pitch as m21pitch
            root_pc = m21pitch.Pitch(chord_root).pitchClass
        except Exception:
            root_pc = -1
        is_diatonic = root_pc in scale_pcs

        non_diatonic_type: str | None = None
        if not is_diatonic:
            # Rough heuristic: if quality is dominant7 and resolves down a 5th it's secondary dominant
            if chord_quality in ("dominant-seventh", "dominant"):
                non_diatonic_type = "secondary_dominant"
            else:
                non_diatonic_type = "borrowed"

        return (numeral, is_diatonic, non_diatonic_type)
    except Exception:
        return ("?", True, None)


def detect_all(chords: list[ParsedChord], key_name: str, mode: str) -> list[ChordAnalysis]:
    results: list[ChordAnalysis] = []

    for parsed in chords:
        midi_pitches = [n.midi_pitch for n in parsed.notes if n.midi_pitch is not None]
        chord_name, root, quality = _midi_to_chord(midi_pitches)

        numeral, is_diatonic, non_diatonic_type = _roman_numeral(root, quality, key_name, mode)

        # Use raw_label if available and chord detection failed
        if chord_name == "Unknown" and parsed.raw_label:
            chord_name = parsed.raw_label
            root = parsed.raw_label[0]

        scales = suggest_scales(root, quality, key_name, mode)

        # Guide tones: root, 3rd, 5th
        guide_tones = _guide_tones(midi_pitches, root)

        results.append(ChordAnalysis(
            position=parsed.position,
            chord_name=chord_name,
            root=root,
            quality=quality,
            roman_numeral=numeral,
            is_diatonic=is_diatonic,
            non_diatonic_type=non_diatonic_type,
            scales=scales,
            guide_tones=guide_tones,
        ))

    return results


def _guide_tones(midi_pitches: list[int], root: str) -> list[str]:
    if not midi_pitches:
        return [root]
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    unique_pcs = sorted({p % 12 for p in midi_pitches})
    return [note_names[pc] for pc in unique_pcs[:4]]
