from fastapi import APIRouter, HTTPException

from backend.models.tab import TabInput
from backend.models.analysis import TheoryAnalysis
from backend.models.response import EnrichedOutput
from backend.parser import tab_parser
from backend.theory import key_detector, chord_detector
from backend.llm import client as llm_client

router = APIRouter()


@router.post("/analyze", response_model=EnrichedOutput)
async def analyze_tab(body: TabInput) -> EnrichedOutput:
    if not body.tab_text.strip():
        raise HTTPException(status_code=400, detail="tab_text is empty")

    # 1. Parse ASCII tab into structured chords
    parsed_chords = tab_parser.parse(body.tab_text, body.tuning, body.capo)
    if not parsed_chords:
        raise HTTPException(status_code=422, detail="Could not parse any chords from the tab. Check formatting.")

    # 2. Detect key
    key_name, mode, confidence = key_detector.detect(parsed_chords)

    # 3. Detect chords + Roman numerals + scale suggestions
    chord_analyses = chord_detector.detect_all(parsed_chords, key_name, mode)

    # 4. Build theory analysis model
    numerals = [c.roman_numeral for c in chord_analyses]
    theory = TheoryAnalysis(
        key=key_name,
        mode=mode,
        key_confidence=confidence,
        chords=chord_analyses,
        progression_numerals=numerals,
        has_borrowed_chords=any(c.non_diatonic_type == "borrowed" for c in chord_analyses),
        has_secondary_dominants=any(c.non_diatonic_type == "secondary_dominant" for c in chord_analyses),
        has_modulation=False,  # modulation detection is a future feature
    )

    # 5. Call LLM for educational explanation
    result = llm_client.generate_explanation(theory, body.tab_text, provider=body.provider)
    return result
