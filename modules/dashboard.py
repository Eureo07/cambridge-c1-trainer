"""
dashboard.py — Visual progress dashboard in the terminal.
"""

from modules.progress import get_streak, get_weekly_stats, get_vocab_stats, get_weak_grammar_structures

def progress_bar(correct: int, total: int, width: int = 20) -> str:
    if total == 0:
        return "░" * width + "  0%"
    ratio = correct / total
    filled = round(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar}  {ratio*100:.0f}%"

def run():
    streak = get_streak()
    weekly = get_weekly_stats()
    vocab = get_vocab_stats()
    weak = get_weak_grammar_structures()

    print("\n" + "═"*55)
    print("  📊 CAMBRIDGE C1 TRAINER — DASHBOARD")
    print("═"*55)

    # Streak
    fire = "🔥" * min(streak, 7)
    print(f"\n  🗓️  Study streak: {streak} day{'s' if streak != 1 else ''}  {fire}")

    # Vocabulary
    print(f"\n  📚 VOCABULARY")
    print(f"  Total cards:   {vocab['total']}")
    print(f"  Mature (≥5):   {vocab['mature']}  {progress_bar(vocab['mature'], vocab['total'])}")
    print(f"  Due today:     {vocab['due_today']}")

    # Weekly activity
    if weekly:
        print(f"\n  📈 THIS WEEK")
        activities = {
            "vocabulary":     "Vocabulary",
            "grammar":        "Grammar   ",
            "writing":        "Writing   ",
            "use_of_english": "UoE       ",
        }
        for key, label in activities.items():
            if key in weekly:
                s = weekly[key]
                acc = s["total_correct"] / s["total_items"] if s["total_items"] else 0
                bar = progress_bar(s["total_correct"], s["total_items"])
                print(f"  {label}  {bar}  ({s['total_items']} items)")
    else:
        print("\n  📈 No activity this week yet. Let's get started!")

    # Weak grammar
    if weak:
        print(f"\n  ⚠️  GRAMMAR STRUCTURES TO REVIEW")
        for s in weak:
            acc_pct = s["accuracy"] * 100
            print(f"  • {s['structure'].replace('_', ' '):<30} {acc_pct:.0f}% accuracy  ({s['attempts']} attempts)")

    # Exam readiness estimate
    print(f"\n  🎯 EXAM READINESS")
    total_items = sum(s["total_items"] for s in weekly.values()) if weekly else 0
    vocab_maturity = vocab["mature"] / vocab["total"] if vocab["total"] else 0

    if total_items < 30 or vocab_maturity < 0.2:
        level = "🔴 Early stage — keep building daily habits"
    elif total_items < 100 or vocab_maturity < 0.5:
        level = "🟡 Progressing — focus on weak areas above"
    else:
        level = "🟢 On track — consider a mock exam soon"

    print(f"  {level}")

    print("\n" + "═"*55)
    input("\n  [Press Enter to continue]")
