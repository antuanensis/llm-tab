import pytest
from pathlib import Path
from backend.parser.tab_parser import parse


SAMPLE_TAB = (Path(__file__).parent / "fixtures" / "sample_tab.txt").read_text()


def test_parse_returns_four_chords():
    chords = parse(SAMPLE_TAB)
    assert len(chords) == 4, f"Expected 4 chords, got {len(chords)}"


def test_parse_chord_labels():
    chords = parse(SAMPLE_TAB)
    labels = [c.raw_label for c in chords]
    assert labels == ["G", "C", "D", "Em"]


def test_parse_g_chord_has_correct_notes():
    chords = parse(SAMPLE_TAB)
    g_chord = chords[0]
    # G major open: e=3(G4), B=0(B3), G=0(G3), D=0(D3), A=2(B2), E=3(G2)
    frets = {n.string_name: n.fret for n in g_chord.notes}
    assert frets.get("e") == 3
    assert frets.get("B") == 0


def test_parse_muted_strings_excluded():
    chords = parse(SAMPLE_TAB)
    # C chord: A=3, E=x (muted) — E string should not appear
    c_chord = chords[1]
    string_names = {n.string_name for n in c_chord.notes}
    assert "E" not in string_names  # low-E is muted on C


def test_parse_midi_pitches_populated():
    chords = parse(SAMPLE_TAB)
    for chord in chords:
        for note in chord.notes:
            if note.fret is not None:
                assert note.midi_pitch is not None
