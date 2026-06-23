"""
writing.py — Writing practice with AI feedback.

CAE Writing paper (Part 1 + Part 2):
  Part 1: Essay (compulsory) — 220-260 words, discursive
  Part 2 (choose one):
    - Letter / Email (formal or semi-formal)
    - Report
    - Review
    - Proposal

Marking criteria (CAE official):
  - Content (task completion)
  - Communicative Achievement (register, effect on reader)
  - Organisation (cohesion, coherence, paragraphing)
  - Language (range, accuracy, C1 vocabulary/grammar)
"""

import os
from modules import ai_client

TASK_TYPES = {
    "1": ("Essay", "essay"),
    "2": ("Formal Letter / Email", "formal_letter"),
    "3": ("Report", "report"),
    "4": ("Review", "review"),
    "5": ("Proposal", "proposal"),
}

PROMPTS = {
    "essay": """Write a CAE Part 1 essay (220-260 words) based on this prompt:

Some people believe that the ability to work remotely has had more negative effects on society than positive ones. Discuss both views and give your own opinion.

Notes:
• productivity and work-life balance
• impact on social skills and teamwork
• urban vs rural economic effects
""",
    "formal_letter": """Write a formal letter (220-260 words) in response to this:

You have read an article in a business magazine claiming that financial literacy should be a compulsory subject in all secondary schools. Write a letter to the editor expressing your views on this issue and suggesting how it could be implemented.
""",
    "report": """Write a report (220-260 words) for the following situation:

Your company has asked you to write a report on the effectiveness of the recent employee training programme and to recommend improvements for future programmes.
""",
    "review": """Write a review (220-260 words):

You have recently attended a professional conference or seminar related to your field. Write a review for a professional magazine describing the event and saying whether you would recommend it to others.
""",
    "proposal": """Write a proposal (220-260 words):

Your town council is considering ways to attract more international investment and tourism. Write a proposal for the council suggesting two or three specific initiatives and explaining how they would benefit the local community.
""",
}

ASSESSMENT_PROMPT = """You are an experienced Cambridge CAE examiner. 
Assess the following student writing sample using the official CAE marking criteria.

Task type: {task_type}
Word count target: 220-260 words

Student's text:
---
{student_text}
---

Provide detailed feedback in this exact JSON format:
{{
  "word_count": <actual count>,
  "scores": {{
    "content": {{"score": <0-5>, "comment": "..."}},
    "communicative_achievement": {{"score": <0-5>, "comment": "..."}},
    "organisation": {{"score": <0-5>, "comment": "..."}},
    "language": {{"score": <0-5>, "comment": "..."}}
  }},
  "total": <sum of 4 scores, max 20>,
  "cae_grade": "<Pass with Merit / Pass / Narrow Fail / Fail>",
  "strengths": ["...", "..."],
  "improvements": ["...", "..."],
  "corrected_sentences": [
    {{"original": "...", "corrected": "...", "explanation": "..."}}
  ],
  "c1_vocabulary_suggestions": ["replace X with Y", "..."],
  "model_opening": "A stronger opening paragraph would be: ..."
}}"""

def get_task_prompt(task_key: str) -> str:
    return PROMPTS.get(task_key, PROMPTS["essay"])

def assess_writing(student_text: str, task_type: str) -> dict:
    prompt = ASSESSMENT_PROMPT.format(task_type=task_type, student_text=student_text)
    response = ai_client.call(prompt, max_tokens=1500)
    import json, re
    try:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"raw_feedback": response}

def display_feedback(feedback: dict):
    if "raw_feedback" in feedback:
        print(feedback["raw_feedback"])
        return

    print("\n" + "═"*55)
    print("  📊 CAE WRITING ASSESSMENT")
    print("═"*55)
    print(f"  Word count: {feedback.get('word_count', '?')} (target: 220-260)")
    print(f"  CAE Grade:  {feedback.get('cae_grade', '?')}")
    print(f"  Total:      {feedback.get('total', '?')} / 20\n")

    scores = feedback.get("scores", {})
    criteria = ["content", "communicative_achievement", "organisation", "language"]
    for c in criteria:
        if c in scores:
            s = scores[c]
            label = c.replace("_", " ").title()
            bar = "█" * s["score"] + "░" * (5 - s["score"])
            print(f"  {label:<30} [{bar}] {s['score']}/5")
            print(f"    → {s['comment']}")

    print("\n  ✅ STRENGTHS")
    for s in feedback.get("strengths", []):
        print(f"    • {s}")

    print("\n  🎯 IMPROVEMENTS NEEDED")
    for i in feedback.get("improvements", []):
        print(f"    • {i}")

    corrections = feedback.get("corrected_sentences", [])
    if corrections:
        print("\n  🔧 LANGUAGE CORRECTIONS")
        for c in corrections[:4]:
            print(f"    ✗ {c.get('original', '')}")
            print(f"    ✓ {c.get('corrected', '')}")
            print(f"    ℹ️  {c.get('explanation', '')}\n")

    vocab = feedback.get("c1_vocabulary_suggestions", [])
    if vocab:
        print("\n  📈 VOCABULARY UPGRADE")
        for v in vocab[:5]:
            print(f"    • {v}")

    model = feedback.get("model_opening", "")
    if model:
        print(f"\n  ✍️  MODEL OPENING:\n    {model}")

    print("═"*55)

def run(quick: bool = False, n: int = 1):
    print("\n✍️  WRITING — CAE Practice")
    print("\n  Task types:")
    for k, (name, _) in TASK_TYPES.items():
        print(f"    {k}. {name}")

    choice = input("\n  Select task type (or Enter for essay): ").strip() or "1"
    task_name, task_key = TASK_TYPES.get(choice, ("Essay", "essay"))

    print(f"\n  📋 TASK: {task_name}")
    print(f"\n{get_task_prompt(task_key)}")
    print("\n  Write your response below.")
    print("  (Type your text. When done, type END on a new line and press Enter)\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    student_text = "\n".join(lines).strip()
    if not student_text:
        print("  No text entered.")
        return

    word_count = len(student_text.split())
    print(f"\n  [{word_count} words] — Sending to examiner AI...\n")

    feedback = assess_writing(student_text, task_name)
    display_feedback(feedback)

    from modules.progress import log_activity
    score = feedback.get("total", 0)
    log_activity("writing", 1, 1 if score >= 12 else 0)

    save = input("\n  Save feedback to file? (y/n): ").strip().lower()
    if save == "y":
        from datetime import datetime
        filename = f"writing_{task_key}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        path = os.path.join(os.path.dirname(__file__), f"../data/progress/{filename}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(f"TASK: {task_name}\n\n")
            f.write(f"YOUR TEXT:\n{student_text}\n\n")
            f.write(f"FEEDBACK:\n{str(feedback)}")
        print(f"  Saved to {filename}")
