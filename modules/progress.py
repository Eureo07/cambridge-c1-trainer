"""
progress.py & dashboard.py — Progress tracking, streaks, and stats.
"""

from datetime import date, timedelta
from modules.db import get_db

def log_activity(activity: str, items: int, correct: int):
    db = get_db()
    db.execute(
        "INSERT INTO activity_log (activity, items, correct) VALUES (?, ?, ?)",
        (activity, items, correct)
    )
    db.commit()

def log_session(duration_min: int = 30, notes: str = ""):
    db = get_db()
    db.execute(
        "INSERT INTO sessions (date, duration_min, notes) VALUES (date('now'), ?, ?)",
        (duration_min, notes)
    )
    db.commit()

def get_streak() -> int:
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT date(created_at) as d FROM activity_log ORDER BY d DESC"
    ).fetchall()
    if not rows:
        return 0
    streak = 0
    check = date.today()
    for row in rows:
        d = date.fromisoformat(row["d"])
        if d == check:
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return streak

def get_weekly_stats() -> dict:
    db = get_db()
    seven_days_ago = str(date.today() - timedelta(days=7))
    rows = db.execute(
        """SELECT activity,
                  SUM(items) as total_items,
                  SUM(correct) as total_correct,
                  COUNT(*) as sessions
           FROM activity_log
           WHERE created_at >= ?
           GROUP BY activity""",
        (seven_days_ago,)
    ).fetchall()
    return {r["activity"]: dict(r) for r in rows}

def get_vocab_stats() -> dict:
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM vocabulary").fetchone()[0]
    mature = db.execute("SELECT COUNT(*) FROM vocabulary WHERE repetitions >= 5").fetchone()[0]
    due_today = db.execute(
        "SELECT COUNT(*) FROM vocabulary WHERE next_review <= date('now')"
    ).fetchone()[0]
    return {"total": total, "mature": mature, "due_today": due_today}

def get_weak_grammar_structures() -> list:
    db = get_db()
    rows = db.execute(
        """SELECT structure,
                  SUM(correct) * 1.0 / COUNT(*) as accuracy,
                  COUNT(*) as attempts
           FROM grammar_log
           GROUP BY structure
           HAVING attempts >= 3
           ORDER BY accuracy ASC LIMIT 5"""
    ).fetchall()
    return [dict(r) for r in rows]
