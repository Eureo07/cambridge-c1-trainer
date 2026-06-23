"""
Cambridge C1 Advanced Trainer
==============================
Designed for a B2-level speaker recovering fluency and targeting C1 (CAE).
Covers: Vocabulary, Grammar, Writing, Reading, Use of English, Progress tracking.
"""

import os
import sys
from modules import vocabulary, grammar, writing, use_of_english, progress, dashboard

MENU = """
╔══════════════════════════════════════════════╗
║        CAMBRIDGE C1 ADVANCED TRAINER         ║
║              powered by Claude API           ║
╠══════════════════════════════════════════════╣
║  1. Vocabulary  (flashcards + spaced rep.)   ║
║  2. Grammar     (B2→C1 structures)           ║
║  3. Writing     (essays, letters, reports)   ║
║  4. Use of English (transformations, gaps)   ║
║  5. Dashboard   (progress & streaks)         ║
║  6. Daily session (auto-mix 30 min)          ║
║  0. Exit                                     ║
╚══════════════════════════════════════════════╝
"""

def main():
    print(MENU)
    while True:
        choice = input("Select an option: ").strip()
        if choice == "1":
            vocabulary.run()
        elif choice == "2":
            grammar.run()
        elif choice == "3":
            writing.run()
        elif choice == "4":
            use_of_english.run()
        elif choice == "5":
            dashboard.run()
        elif choice == "6":
            daily_session()
        elif choice == "0":
            print("See you tomorrow! Keep going. 💪")
            sys.exit(0)
        else:
            print("Invalid option.")
        print(MENU)

def daily_session():
    """30-minute auto-mixed session: vocab + grammar + use of english."""
    print("\n🗓️  Starting daily session (approx. 30 min)...")
    vocabulary.run(quick=True, n=10)
    grammar.run(quick=True, n=3)
    use_of_english.run(quick=True, n=5)
    progress.log_session()
    print("\n✅ Daily session complete! Check your dashboard for updated stats.")

if __name__ == "__main__":
    main()
