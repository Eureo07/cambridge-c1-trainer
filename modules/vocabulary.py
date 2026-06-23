"""
vocabulary.py — Flashcard system with SM-2 spaced repetition
Targets C1 academic, professional, and idiomatic vocabulary.
"""

import json
import os
import random
from datetime import date, timedelta
from modules.db import get_db

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/vocabulary")

# ── SM-2 algorithm ───────────────────────────────────────────────────────────

def sm2_update(card: dict, quality: int) -> dict:
    """
    Update card scheduling using SM-2 algorithm.
    quality: 0-2 = fail (Again), 3 = hard, 4 = good, 5 = easy
    """
    if quality < 3:
        card["repetitions"] = 0
        card["interval"] = 1
    else:
        if card["repetitions"] == 0:
            card["interval"] = 1
        elif card["repetitions"] == 1:
            card["interval"] = 6
        else:
            card["interval"] = round(card["interval"] * card["easiness"])

        card["repetitions"] += 1
        card["easiness"] = max(1.3, card["easiness"] + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    card["next_review"] = str(date.today() + timedelta(days=card["interval"]))
    return card

# ── Card loader ───────────────────────────────────────────────────────────────

def load_due_cards(deck: str = "c1_core", limit: int = 20) -> list:
    db = get_db()
    today = str(date.today())
    rows = db.execute(
        """SELECT * FROM vocabulary
           WHERE deck = ? AND next_review <= ?
           ORDER BY next_review ASC LIMIT ?""",
        (deck, today, limit)
    ).fetchall()
    return [dict(r) for r in rows]

def load_new_cards(deck: str = "c1_core", limit: int = 5) -> list:
    db = get_db()
    rows = db.execute(
        """SELECT * FROM vocabulary
           WHERE deck = ? AND repetitions = 0
           ORDER BY RANDOM() LIMIT ?""",
        (deck, limit)
    ).fetchall()
    return [dict(r) for r in rows]

# ── Session ───────────────────────────────────────────────────────────────────

def review_card(card: dict) -> int:
    """Show a card and collect user quality rating. Returns quality 0-5."""
    print(f"\n{'─'*50}")
    print(f"  Word:    {card['word']}")
    print(f"  Context: {card['example']}")
    print(f"{'─'*50}")
    input("  [Press Enter to reveal] ")
    print(f"\n  Definition: {card['definition']}")
    print(f"  Synonyms:   {card['synonyms']}")
    print(f"  Register:   {card['register']}")
    print(f"\n  How well did you know it?")
    print("  0=Again  3=Hard  4=Good  5=Easy")
    while True:
        q = input("  → ").strip()
        if q in {"0", "3", "4", "5"}:
            return int(q)

def run(quick: bool = False, n: int = 20):
    db = get_db()
    print("\n📚 VOCABULARY — Spaced Repetition")
    due = load_due_cards(limit=n)
    new = load_new_cards(limit=5) if not quick else []
    cards = due + new

    if not cards:
        print("  No cards due today. Come back tomorrow!")
        return

    correct = 0
    for card in cards:
        quality = review_card(card)
        updated = sm2_update(card, quality)
        if quality >= 4:
            correct += 1
        db.execute(
            """UPDATE vocabulary SET repetitions=?, interval=?, easiness=?, next_review=?
               WHERE id=?""",
            (updated["repetitions"], updated["interval"],
             updated["easiness"], updated["next_review"], card["id"])
        )
        db.commit()

    print(f"\n  Session done: {correct}/{len(cards)} correct.")
    from modules.progress import log_activity
    log_activity("vocabulary", len(cards), correct)
