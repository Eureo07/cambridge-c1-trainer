# OpenCode Rules — Cambridge C1 Trainer

## Project context
This is a Python CLI application for Cambridge C1 Advanced (CAE) exam preparation.
The user is a Spanish native speaker (B2 level, recovering from inactivity) targeting C1.

## Code conventions
- Pure Python stdlib where possible (no heavy dependencies)
- All AI calls go through `modules/ai_client.py` — never call the API directly from other modules
- All database access goes through `modules/db.py` — never open SQLite connections elsewhere
- Always call `from modules.progress import log_activity` at the end of exercise sessions
- Use `print()` for all terminal output — no external TUI libraries unless explicitly requested
- SM-2 spaced repetition algorithm lives only in `modules/vocabulary.py`

## Data model
- SQLite database at `data/trainer.db`
- Vocabulary table: word, definition, example, synonyms, register, deck, SM-2 fields
- Grammar log: structure name + correct (0/1) per attempt
- Activity log: activity name, items, correct, timestamp
- Sessions: date, duration, notes

## Exercise generation pattern
When adding a new exercise type:
1. Define a prompt constant at the top of the module
2. Call `ai_client.call(prompt)` and parse the JSON response with regex fallback
3. Handle parse errors gracefully — print a warning, don't crash
4. Log results with `log_activity()`

## CAE exam structure to keep in mind
- Paper 1: Reading & Use of English (Parts 1-8) — 90 min
- Paper 2: Writing (Part 1 essay + Part 2 choice) — 90 min  
- Paper 3: Listening (Parts 1-4) — ~40 min
- Paper 4: Speaking (Parts 1-4) — ~15 min per pair

## Phase priorities
- Phase 1 (current): vocabulary flashcards, grammar B2 review, key word transformations, writing
- Phase 2: C1 grammar structures, word formation, multiple-choice cloze
- Phase 3: listening module, speaking prompts, full mock exams
