"""
grammar.py — Grammar exercises targeting B2→C1 gap structures.

Key C1 areas vs B2:
  - Inversion (Not only did..., Hardly had...)
  - Mixed conditionals (If I had studied..., I would be...)
  - Cleft sentences (It was John who..., What I need is...)
  - Subjunctive (I suggest he be..., It is vital that...)
  - Advanced modals (must have been, needn't have, should have)
  - Participle clauses (Having finished..., Being exhausted...)
  - Passive with reporting verbs (It is believed that..., He is said to...)
"""

import json
import os
import random
from modules.db import get_db
from modules import ai_client

STRUCTURES = [
    "inversion",
    "mixed_conditionals",
    "cleft_sentences",
    "subjunctive",
    "advanced_modals",
    "participle_clauses",
    "passive_reporting",
    "relative_clauses_advanced",
    "hedging_language",
    "discourse_markers",
]

STRUCTURE_DESCRIPTIONS = {
    "inversion": "Negative adverbials at the start of a sentence trigger subject-auxiliary inversion. (Never have I seen... / Not only did she...)",
    "mixed_conditionals": "Mixing past and present time references across condition and result clauses.",
    "cleft_sentences": "Emphasising a specific part of a sentence using 'It is/was... that/who' or 'What...'",
    "subjunctive": "Formal structures requiring base form after suggest/insist/recommend/demand + that.",
    "advanced_modals": "Deduction and speculation about past events (must have, can't have, should have, needn't have).",
    "participle_clauses": "Replacing full clauses with -ing or -ed participle constructions for concision.",
    "passive_reporting": "Impersonal passive with reporting verbs: It is said/believed/thought that... / He is known to have...",
    "relative_clauses_advanced": "Non-defining relative clauses, reduced relatives, preposition + which/whom.",
    "hedging_language": "Expressing uncertainty formally: It would appear that... / This may suggest... / There is a tendency to...",
    "discourse_markers": "Connecting ideas at C1 level: Nevertheless, Furthermore, In spite of this, Notwithstanding...",
}

def generate_exercise(structure: str, difficulty: str = "C1") -> dict:
    """Call Claude API to generate a grammar exercise for the given structure."""
    prompt = f"""Generate a grammar exercise for Cambridge C1 Advanced (CAE) exam preparation.

Structure: {structure}
Description: {STRUCTURE_DESCRIPTIONS.get(structure, '')}
Difficulty: {difficulty}

Return ONLY valid JSON with this exact format:
{{
  "instruction": "Brief instruction for the student",
  "question": "The exercise sentence or prompt",
  "answer": "The correct answer",
  "explanation": "Why this answer is correct (2-3 sentences, mention the grammar rule)",
  "tip": "One exam tip for this structure in CAE"
}}"""

    response = ai_client.call(prompt)
    try:
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"error": "Could not parse exercise", "raw": response}

def run_exercise(exercise: dict) -> bool:
    """Display exercise and return True if answered correctly."""
    if "error" in exercise:
        print(f"  ⚠️  {exercise['error']}")
        return False

    print(f"\n{'─'*55}")
    print(f"  📝 {exercise['instruction']}")
    print(f"\n  {exercise['question']}")
    print(f"{'─'*55}")
    user_answer = input("  Your answer: ").strip()

    correct = exercise["answer"].strip().lower()
    is_correct = user_answer.lower() == correct or correct in user_answer.lower()

    if is_correct:
        print("  ✅ Correct!")
    else:
        print(f"  ❌ Answer: {exercise['answer']}")

    print(f"\n  📖 {exercise['explanation']}")
    print(f"  💡 Exam tip: {exercise['tip']}")
    return is_correct

def run(quick: bool = False, n: int = 5):
    print("\n🧠 GRAMMAR — B2→C1 Structures")

    # Prioritise structures where user has most errors
    db = get_db()
    rows = db.execute(
        """SELECT structure, SUM(correct) as c, COUNT(*) as total
           FROM grammar_log GROUP BY structure"""
    ).fetchall()

    weak = [r["structure"] for r in rows if r["c"] / r["total"] < 0.6] if rows else []
    pool = weak if weak else STRUCTURES
    selected = random.sample(pool, min(n, len(pool)))

    correct_count = 0
    for structure in selected:
        print(f"\n  Structure: {structure.replace('_', ' ').upper()}")
        exercise = generate_exercise(structure)
        if run_exercise(exercise):
            correct_count += 1
        db.execute(
            "INSERT INTO grammar_log (structure, correct) VALUES (?, ?)",
            (structure, 1 if correct_count else 0)
        )
        db.commit()
        if not quick:
            input("\n  [Enter for next] ")

    print(f"\n  Grammar session: {correct_count}/{len(selected)} correct.")
    from modules.progress import log_activity
    log_activity("grammar", len(selected), correct_count)
