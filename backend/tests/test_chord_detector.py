import pytest
from backend.parser.tab_parser import parse
from backend.theory import key_detector, chord_detector
from pathlib import Path


SAMPLE_TAB = (Path(__file__).parent / "fixtures" / "sample_tab.txt").read_text()


def test_key_detection():
    chords = parse(SAMPLE_TAB)
    key_name, mode, confidence = key_detector.detect(chords)
    assert key_name == "G"
    assert mode == "major"
    assert confidence > 0.5


def test_chord_names():
    chords = parse(SAMPLE_TAB)
    key_name, mode, _ = key_detector.detect(chords)
    analyses = chord_detector.detect_all(chords, key_name, mode)
    roots = [a.root for a in analyses]
    assert "G" in roots
    assert "E" in roots  # Em


def test_chord_count():
    chords = parse(SAMPLE_TAB)
    analyses = chord_detector.detect_all(chords, "G", "major")
    assert len(analyses) == 4
