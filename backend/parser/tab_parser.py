"""
ASCII guitar tab parser.

Handles the common 6-line tablature format:
    e|---3---0---2---0---
    B|---0---1---3---0---
    G|---0---0---2---0---
    D|---0---2---0---2---
    A|---2---3---x---2---
    E|---3---x---x---0---

String indices are assigned by order of appearance in the file (0 = top line,
5 = bottom line), not by letter label. This correctly handles drop-D tabs
where the low string is labeled "D" instead of "E".

Returns a list of ParsedChord objects, one per vertical time-slice.
"""
import re
from typing import Optional

from backend.models.tab import ParsedNote, ParsedChord
from backend.parser.tuning import TUNINGS, STRING_NAME_TO_INDEX, STRING_NAMES

# A valid tab line: optional leading whitespace, a string letter, optional
# whitespace, then | or : followed by the fret content.
_TAB_LINE_RE = re.compile(r"^\s*([eBGDAe])\s*[|:](.+)", re.IGNORECASE)

# Chord label line: a line of whitespace + chord names (no | character)
_CHORD_LABEL_RE = re.compile(r"^[\s]*(([A-G][#b]?(?:m|maj|min|dim|aug|sus|add|7|9|11|13)?[\s/]*)+)$")


def _midi_pitch(string_index: int, fret: Optional[int], tuning: dict[int, int]) -> Optional[int]:
    if fret is None or string_index not in tuning:
        return None
    return tuning[string_index] + fret


def _tokenize_string_line(content: str) -> list[Optional[int]]:
    """
    Turn a raw string-line content (after the '|') into a list of fret values
    aligned to position indices.

    '-' → -1 (spacer / no note)
    digit(s) → fret number
    'x'/'X' → None (muted)
    ornaments (h, p, b, /, \\) → -1 (skip, keep alignment)
    """
    tokens: list[Optional[int]] = []
    i = 0
    while i < len(content):
        ch = content[i]
        if ch == "-":
            tokens.append(-1)
            i += 1
        elif ch in "xX":
            tokens.append(None)
            i += 1
        elif ch.isdigit():
            j = i + 1
            while j < len(content) and content[j].isdigit():
                j += 1
            tokens.append(int(content[i:j]))
            i = j
        else:
            # ornament characters (h, p, b, /, \, |) — treat as spacer
            tokens.append(-1)
            i += 1
    return tokens


def _extract_chord_labels(lines: list[str]) -> list[str]:
    """
    If there is a chord-label line (e.g., '  G   C   D  Em') below the tab
    grid, extract the chord names in order.
    """
    for line in lines:
        stripped = line.strip()
        if stripped and "|" not in stripped:
            parts = stripped.split()
            if parts and all(re.match(r"^[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|\d)*$", p) for p in parts):
                return parts
    return []


def parse(tab_text: str, tuning_name: str = "standard", capo: int = 0) -> list[ParsedChord]:
    """
    Parse an ASCII tab string into a list of ParsedChord objects.
    """
    base_tuning = TUNINGS.get(tuning_name, TUNINGS["standard"])
    tuning = {k: v + capo for k, v in base_tuning.items()}

    lines = tab_text.splitlines()

    # Collect tab lines in order of appearance.
    # String index = position in the file (0 = top = highest string).
    # This is more robust than letter-based lookup: handles drop-D (two "D"
    # lines), alternate tunings with unusual labels, etc.
    tab_line_candidates: list[tuple[int, str, str]] = []  # (line_num, letter, content)
    other_lines: list[str] = []

    for line_num, line in enumerate(lines):
        m = _TAB_LINE_RE.match(line)
        if m:
            tab_line_candidates.append((line_num, m.group(1), m.group(2)))
        else:
            other_lines.append(line)

    # Take at most 6 consecutive tab lines
    tab_lines = tab_line_candidates[:6]

    if len(tab_lines) < 4:
        return []

    chord_labels = _extract_chord_labels(other_lines)

    # Build a display name for each string position.
    # When two strings share a label (e.g. drop-D has two "D" lines),
    # suffix the second one to keep them distinct in output.
    seen_letters: dict[str, int] = {}
    string_display_names: dict[int, str] = {}
    for order_idx, (_, letter, _content) in enumerate(tab_lines):
        canonical = letter.lower() if letter.lower() == "e" and order_idx == 0 else letter.upper()
        count = seen_letters.get(canonical, 0)
        seen_letters[canonical] = count + 1
        string_display_names[order_idx] = canonical if count == 0 else f"{canonical}{count + 1}"

    # Tokenize
    tokenized: dict[int, list[Optional[int]]] = {}
    for order_idx, (_, _letter, content) in enumerate(tab_lines):
        tokenized[order_idx] = _tokenize_string_line(content)

    # Pad all strings to the same length
    max_len = max(len(t) for t in tokenized.values())
    for idx in tokenized:
        while len(tokenized[idx]) < max_len:
            tokenized[idx].append(-1)

    active_indices = list(tokenized.keys())

    # Collect time slices: positions where at least one string has a real note
    chords: list[ParsedChord] = []
    chord_label_idx = 0
    i = 0
    while i < max_len:
        has_note = any(tokenized[idx][i] != -1 for idx in active_indices)

        if has_note:
            notes: list[ParsedNote] = []
            for order_idx in active_indices:
                fret = tokenized[order_idx][i]
                if fret == -1:
                    continue
                midi = _midi_pitch(order_idx, fret, tuning)
                notes.append(ParsedNote(
                    string_name=string_display_names[order_idx],
                    string_index=order_idx,
                    fret=fret,
                    midi_pitch=midi,
                ))
            if notes:
                label = chord_labels[chord_label_idx] if chord_label_idx < len(chord_labels) else None
                chords.append(ParsedChord(position=i, notes=notes, raw_label=label))
                chord_label_idx += 1

            # Advance past this note cluster
            i += 1
            while i < max_len and any(tokenized[idx][i] != -1 for idx in active_indices):
                i += 1
        else:
            i += 1

    return chords
