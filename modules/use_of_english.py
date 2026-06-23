"""
use_of_english.py — CAE Use of English (Paper 1: Parts 1-4)

Part 1: Multiple-choice cloze (8 gaps, 4 options each) — vocabulary in context
Part 2: Open cloze (8 gaps) — grammar & vocabulary, no options
Part 3: Word formation (8 gaps) — derive correct form of a given word
Part 4: Key word transformations (6 items) — rewrite keeping meaning, using keyword
"""

import json
import random
from modules import ai_client
from modules.db import get_db

PARTS = {
    "1": "Multiple-choice cloze",
    "2": "Open cloze",
    "3": "Word formation",
    "4": "Key word transformation",
}

PART_PROMPTS = {
    "1": """Create a CAE Part 1 multiple-choice cloze exercise.
Write a short paragraph (4-6 sentences) on a topic suitable for C1 level (e.g. environment, technology, society, business).
Include exactly 4 gaps numbered (1)-(4). Each gap tests vocabulary in context.

Return ONLY valid JSON:
{{
  "topic": "...",
  "text": "The paragraph with (1)___, (2)___, (3)___, (4)___ gaps",
  "questions": [
    {{"gap": 1, "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "answer": "A", "explanation": "..."}},
    ...
  ]
}}""",

    "2": """Create a CAE Part 2 open cloze exercise.
Write a paragraph with 5 gaps. Each gap tests a grammar word or common collocation (articles, prepositions, pronouns, auxiliaries, conjunctions, etc.).

Return ONLY valid JSON:
{{
  "topic": "...",
  "text": "Paragraph with (1)___, (2)___, (3)___, (4)___, (5)___ gaps",
  "answers": [
    {{"gap": 1, "answer": "...", "explanation": "..."}},
    ...
  ]
}}""",

    "3": """Create a CAE Part 3 word formation exercise.
Write 5 sentences, each with a gap and a root word in capitals at the end.
The student must form the correct word (noun, verb, adjective, adverb, negative prefix, etc.)

Return ONLY valid JSON:
{{
  "sentences": [
    {{"sentence": "The ___ of the new policy has been widely debated.", "root": "IMPLEMENT", "answer": "implementation", "explanation": "..."}},
    ...
  ]
}}""",

    "4": """Create a CAE Part 4 key word transformation exercise (3 items).
Each item: an original sentence, a key word, and the student must rewrite the second sentence using 3-6 words including the key word.

Common targets: inversion, passive, reported speech, conditionals, comparatives, phrasal verbs, modal perfects.

Return ONLY valid JSON:
{{
  "items": [
    {{
      "sentence": "They cancelled the meeting because of the storm.",
      "keyword": "OWING",
      "incomplete": "The meeting was cancelled ___ the storm.",
      "answer": "owing to",
      "full_answer": "The meeting was cancelled owing to the storm.",
      "explanation": "OWING TO = because of (formal). The preposition phrase replaces the causal clause.",
      "structure_tested": "formal_prepositions"
    }},
    ...
  ]
}}"""
}

def generate_exercise(part: str) -> dict:
    prompt = PART_PROMPTS.get(part, PART_PROMPTS["4"])
    response = ai_client.call(prompt, max_tokens=1200)
    import re
    try:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"error": response}

def run_part1(data: dict) -> int:
    print(f"\n  📖 Topic: {data.get('topic', '')}")
    print(f"\n  {data['text']}\n")
    correct = 0
    for q in data["questions"]:
        print(f"  ({q['gap']}) ", end="")
        for letter, word in q["options"].items():
            print(f"  {letter}) {word}", end="   ")
        print()
        answer = input("  → ").strip().upper()
        if answer == q["answer"].upper():
            print(f"  ✅ Correct! ({q['answer']})")
            correct += 1
        else:
            print(f"  ❌ Answer: {q['answer']} — {q['explanation']}")
    return correct

def run_part2(data: dict) -> int:
    print(f"\n  📖 Topic: {data.get('topic', '')}")
    print(f"\n  {data['text']}\n")
    correct = 0
    for a in data["answers"]:
        answer = input(f"  Gap ({a['gap']}): ").strip().lower()
        if answer == a["answer"].lower():
            print(f"  ✅ Correct!")
            correct += 1
        else:
            print(f"  ❌ Answer: {a['answer']} — {a['explanation']}")
    return correct

def run_part3(data: dict) -> int:
    correct = 0
    for s in data["sentences"]:
        print(f"\n  {s['sentence']}")
        print(f"  Root word: {s['root']}")
        answer = input("  Your word: ").strip().lower()
        if answer == s["answer"].lower():
            print("  ✅ Correct!")
            correct += 1
        else:
            print(f"  ❌ Answer: {s['answer']} — {s['explanation']}")
    return correct

def run_part4(data: dict) -> int:
    correct = 0
    for item in data["items"]:
        print(f"\n  Original:  {item['sentence']}")
        print(f"  Keyword:   {item['keyword'].upper()}")
        print(f"  Complete:  {item['incomplete']}")
        answer = input("  Your answer (3-6 words): ").strip().lower()
        correct_ans = item["answer"].lower()
        if answer == correct_ans or correct_ans in answer:
            print(f"  ✅ Correct!")
            correct += 1
        else:
            print(f"  ❌ Answer: {item['answer']}")
            print(f"  Full:   {item['full_answer']}")
            print(f"  📖 {item['explanation']}")
            print(f"  Structure: {item.get('structure_tested', '')}")
    return correct

PART_RUNNERS = {"1": run_part1, "2": run_part2, "3": run_part3, "4": run_part4}

def run(quick: bool = False, n: int = 2):
    print("\n📝 USE OF ENGLISH — CAE Parts 1-4")
    if quick:
        parts = random.sample(["2", "3", "4"], min(n, 3))
    else:
        print("\n  Which part?")
        for k, v in PARTS.items():
            print(f"    {k}. Part {k}: {v}")
        print("    5. Random mix")
        choice = input("  → ").strip()
        parts = list(PARTS.keys()) if choice == "5" else [choice] if choice in PARTS else ["4"]

    total_correct = total_items = 0
    for part in parts:
        print(f"\n  ── Part {part}: {PARTS[part]} ──")
        print("  Generating exercise...")
        data = generate_exercise(part)
        if "error" in data:
            print(f"  ⚠️  Error generating exercise.")
            continue
        runner = PART_RUNNERS.get(part)
        if runner:
            c = runner(data)
            total_correct += c

    from modules.progress import log_activity
    log_activity("use_of_english", total_items or 1, total_correct)
