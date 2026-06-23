# Cambridge C1 Advanced Trainer

A terminal-based study system for the **Cambridge C1 Advanced (CAE)** exam.
Built to be extended iteratively with OpenCode.

---

## Setup

```bash
# 1. Clone / place this folder somewhere
cd cambridge_trainer

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Run
python main.py
```

No external dependencies. Uses Python stdlib + Claude API via HTTP.

---

## Project Structure

```
cambridge_trainer/
├── main.py                    # Entry point & menu
├── modules/
│   ├── ai_client.py           # Claude API wrapper
│   ├── db.py                  # SQLite layer + vocabulary seed
│   ├── vocabulary.py          # Flashcards with SM-2 spaced repetition
│   ├── grammar.py             # B2→C1 grammar exercises (AI-generated)
│   ├── writing.py             # CAE writing practice + AI assessment
│   ├── use_of_english.py      # CAE Parts 1-4 (AI-generated exercises)
│   ├── progress.py            # Activity logging & stats
│   └── dashboard.py           # Terminal dashboard
└── data/
    ├── trainer.db             # SQLite database (auto-created)
    └── progress/              # Saved writing feedback
```

---

## CAE Exam Structure (what this covers)

| Paper | Name | Weight | Covered |
|-------|------|--------|---------|
| 1 | Reading & Use of English | 40% | ✅ Parts 1-4 (UoE) |
| 2 | Writing | 20% | ✅ All task types |
| 3 | Listening | 20% | 🔜 Phase 2 |
| 4 | Speaking | 20% | 🔜 Phase 3 |

---

## Study Roadmap

### Phase 1 — Rust Recovery (Weeks 1-4)
Goal: Get back to solid B2 active level.

| Activity | Daily | Focus |
|----------|-------|-------|
| Vocabulary flashcards | 15 min | 10 cards/day (SM-2) |
| Grammar exercises | 10 min | B2 review: conditionals, passive, modal verbs |
| Use of English Part 4 | 10 min | Key word transformations |
| Writing (x2/week) | 30 min | Emails and short essays |

**Milestone**: Write a 250-word formal email scoring ≥14/20.

---

### Phase 2 — C1 Structures (Weeks 5-10)
Goal: Internalise C1-specific grammar and vocabulary.

| Activity | Daily | Focus |
|----------|-------|-------|
| Vocabulary flashcards | 15 min | 15 cards/day, C1 academic register |
| Grammar — C1 structures | 15 min | Inversion, cleft, subjunctive, hedging |
| Use of English Parts 1-3 | 15 min | Cloze and word formation |
| Writing | 30 min | CAE essays and reports |

**Milestone**: Score ≥70% on Use of English mock (Parts 1-4 combined).

---

### Phase 3 — Exam Simulation (Weeks 11-16)
Goal: Perform consistently at CAE Pass level under timed conditions.

| Activity | Schedule | Notes |
|----------|----------|-------|
| Full mock Reading+UoE | Weekly | 1h 30min timed |
| Full mock Writing | Weekly | 1h 30min timed |
| Speaking practice | 3x/week | Record yourself, self-assess |
| Listening (YouTube/podcasts) | Daily | BBC Radio 4, TED, Economist |
| Vocabulary consolidation | Daily | Review mature cards only |

**Milestone**: Complete a full CAE mock paper and self-mark.

---

## Grammar Structures Covered

| Structure | Level | Priority |
|-----------|-------|----------|
| Inversion (Never have I...) | C1 | ⭐⭐⭐ |
| Mixed conditionals | C1 | ⭐⭐⭐ |
| Cleft sentences (It was... who) | C1 | ⭐⭐⭐ |
| Subjunctive (suggest he be...) | C1 | ⭐⭐ |
| Passive + reporting verbs | B2-C1 | ⭐⭐⭐ |
| Participle clauses | B2-C1 | ⭐⭐ |
| Advanced modals (must have been) | B2-C1 | ⭐⭐⭐ |
| Hedging language | C1 | ⭐⭐ |
| Discourse markers (C1 level) | C1 | ⭐⭐ |
| Relative clauses (advanced) | B2-C1 | ⭐⭐ |

---

## Extending with OpenCode

Suggested next modules to build:

```
# Tell OpenCode:
"Add a listening module that fetches BBC Learning English transcripts 
 and generates comprehension questions using the Claude API."

"Add a speaking module that generates CAE Part 2 image description prompts 
 and provides model answers."

"Add a mock exam mode that runs a full 90-minute timed Use of English + 
 Writing session and generates a full score report."

"Add a vocabulary deck importer that reads a CSV file and populates the 
 database with custom word lists."
```

---

## Recommended External Resources

| Resource | Use for |
|----------|---------|
| Cambridge English website | Official CAE practice tests |
| BBC Learning English | Listening + vocabulary |
| The Economist / Guardian | Reading at C1 level |
| Youglish.com | Pronunciation in context |
| Cambridge English Vocabulary in Use C1 | Systematic vocab study |
| English Grammar in Use (Murphy) | B2 grammar consolidation |
| Advanced Grammar in Use (Hewings) | C1 grammar |

---

## Writing Assessment Criteria (CAE official)

Each piece is marked 0-5 on four criteria (max 20 points):

| Criterion | What examiners look for |
|-----------|------------------------|
| **Content** | All points addressed, appropriate word count |
| **Communicative Achievement** | Correct register, engages the reader |
| **Organisation** | Clear paragraphs, cohesive devices, logical flow |
| **Language** | Range of C1 vocab & grammar, few errors |

Pass threshold: approximately 60% (12/20).

---

*Built for personal use. Extend freely.*
