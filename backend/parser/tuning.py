# MIDI pitch of each open string in standard tuning
# String index: 0 = high-e, 5 = low-E
STANDARD_TUNING = {
    0: 64,  # e  (E4)
    1: 59,  # B  (B3)
    2: 55,  # G  (G3)
    3: 50,  # D  (D3)
    4: 45,  # A  (A2)
    5: 40,  # E  (E2)
}

DROP_D_TUNING = {**STANDARD_TUNING, 5: 38}  # low-E dropped to D2

OPEN_G_TUNING = {
    0: 62,  # D4
    1: 59,  # B3
    2: 55,  # G3
    3: 50,  # D3
    4: 43,  # G2
    5: 38,  # D2
}

TUNINGS: dict[str, dict[int, int]] = {
    "standard": STANDARD_TUNING,
    "drop_d": DROP_D_TUNING,
    "open_g": OPEN_G_TUNING,
}

STRING_NAMES = {0: "e", 1: "B", 2: "G", 3: "D", 4: "A", 5: "E"}

# Map the letter prefix in an ASCII tab line to string index
STRING_NAME_TO_INDEX = {"e": 0, "B": 1, "G": 2, "D": 3, "A": 4, "E": 5}
