"""
db.py — SQLite database layer for Cambridge C1 Trainer.
All data stored locally in data/trainer.db
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/trainer.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS vocabulary (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    word        TEXT NOT NULL,
    definition  TEXT,
    example     TEXT,
    synonyms    TEXT,
    register    TEXT DEFAULT 'neutral',
    deck        TEXT DEFAULT 'c1_core',
    repetitions INTEGER DEFAULT 0,
    interval    INTEGER DEFAULT 1,
    easiness    REAL DEFAULT 2.5,
    next_review TEXT DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS grammar_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    structure   TEXT NOT NULL,
    correct     INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS activity_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    activity    TEXT NOT NULL,
    items       INTEGER DEFAULT 0,
    correct     INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT DEFAULT (date('now')),
    duration_min INTEGER DEFAULT 30,
    notes       TEXT
);
"""

_db = None

def get_db() -> sqlite3.Connection:
    global _db
    if _db is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        _db = sqlite3.connect(DB_PATH, check_same_thread=False)
        _db.row_factory = sqlite3.Row
        _db.executescript(SCHEMA)
        _db.commit()
        _seed_vocabulary_if_empty()
    return _db

def _seed_vocabulary_if_empty():
    """Seed database with starter C1 vocabulary if empty."""
    count = _db.execute("SELECT COUNT(*) FROM vocabulary").fetchone()[0]
    if count > 0:
        return

    seed_words = [
        ("ubiquitous", "present, appearing, or found everywhere", "Smartphones have become ubiquitous in modern society.", "omnipresent, pervasive", "formal", "c1_core"),
        ("ameliorate", "to make something bad or unsatisfactory better", "Measures were taken to ameliorate the working conditions.", "improve, alleviate, mitigate", "formal", "c1_core"),
        ("contentious", "causing or likely to cause argument or controversy", "The new tax policy proved highly contentious.", "controversial, disputed, debatable", "formal", "c1_core"),
        ("pragmatic", "dealing with things sensibly and realistically", "We need a pragmatic approach to solving this problem.", "practical, realistic, sensible", "neutral", "c1_core"),
        ("elusive", "difficult to find, catch, or achieve", "The perfect work-life balance remains elusive for many.", "hard to pin down, fleeting, intangible", "neutral", "c1_core"),
        ("proliferate", "to increase rapidly in number or amount", "Social media platforms have proliferated over the past decade.", "multiply, spread, mushroom", "formal", "c1_core"),
        ("alleviate", "to make suffering, deficiency, or a problem less severe", "This medication should alleviate the pain.", "reduce, ease, relieve, mitigate", "formal", "c1_core"),
        ("endorse", "to declare one's public approval or support of", "The committee endorsed the new proposal unanimously.", "support, back, approve, advocate", "formal", "c1_core"),
        ("intangible", "unable to be touched or grasped; not having physical presence", "The intangible benefits of the programme are hard to measure.", "abstract, incorporeal, immaterial", "formal", "c1_core"),
        ("stringent", "strict, precise, and exacting", "The company must meet stringent environmental standards.", "strict, rigorous, demanding, exacting", "formal", "c1_core"),
        ("nuanced", "characterized by subtle shades of meaning or expression", "The report takes a nuanced view of the issue.", "subtle, refined, sophisticated", "neutral", "c1_core"),
        ("volatile", "liable to change rapidly and unpredictably, especially for the worse", "The volatile market conditions made investors nervous.", "unstable, unpredictable, erratic", "neutral", "c1_core"),
        ("unprecedented", "never done or known before", "The company reported unprecedented levels of growth.", "unparalleled, unheard-of, novel", "formal", "c1_core"),
        ("catalyst", "a person or thing that precipitates an event", "The report acted as a catalyst for reform.", "trigger, stimulus, impetus", "neutral", "c1_core"),
        ("compelling", "evoking interest, attention, or admiration in a powerfully irresistible way", "She made a compelling case for investment.", "convincing, persuasive, forceful, powerful", "neutral", "c1_core"),
        ("mitigate", "make less severe, serious, or painful", "Steps were taken to mitigate the environmental impact.", "reduce, lessen, alleviate, moderate", "formal", "c1_core"),
        ("discrepancy", "a lack of compatibility or similarity between two or more facts", "There is a discrepancy between the two reports.", "inconsistency, difference, gap, divergence", "formal", "c1_core"),
        ("paramount", "more important than anything else; supreme", "Safety is of paramount importance on the construction site.", "supreme, foremost, primary, overriding", "formal", "c1_core"),
        ("detrimental", "tending to cause harm", "Excessive screen time can be detrimental to your health.", "harmful, damaging, injurious, adverse", "formal", "c1_core"),
        ("encompass", "to surround and have or hold within", "The new law encompasses a wide range of offences.", "include, cover, incorporate, embrace", "formal", "c1_core"),
    ]

    _db.executemany(
        "INSERT INTO vocabulary (word, definition, example, synonyms, register, deck) VALUES (?,?,?,?,?,?)",
        seed_words
    )
    _db.commit()
    print(f"  Seeded {len(seed_words)} C1 vocabulary cards.")
