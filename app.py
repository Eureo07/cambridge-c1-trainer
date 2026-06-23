"""
app.py — Flask web server for Cambridge C1 Advanced Trainer.
Wraps existing CLI modules in a REST API and serves a single-page frontend.
"""

import os
import re
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
from modules.db import get_db
from modules import vocabulary, grammar, use_of_english, progress, writing

load_dotenv()

app = Flask(__name__)

get_db()


# ─── Vocabulary API ───────────────────────────────────────────────────────────

@app.route('/api/vocabulary/next')
def api_vocab_next():
    due = vocabulary.load_due_cards(limit=20)
    new = vocabulary.load_new_cards(limit=5)
    combined = due + new

    if not combined:
        return jsonify({'card': None, 'remaining': 0, 'total': 0, 'reviewed': 0})

    card = combined[0]
    remaining = len(combined) - 1
    return jsonify({
        'card': {
            'id': card['id'],
            'word': card['word'],
            'definition': card['definition'],
            'example': card['example'],
            'synonyms': card['synonyms'],
            'register': card['register'],
        },
        'remaining': remaining,
        'total': len(combined),
        'reviewed': 0,
    })


@app.route('/api/vocabulary/review', methods=['POST'])
def api_vocab_review():
    data = request.get_json()
    card_id = data['card_id']
    quality = data['quality']

    db = get_db()
    row = db.execute("SELECT * FROM vocabulary WHERE id = ?", (card_id,)).fetchone()
    if not row:
        return jsonify({'error': 'Card not found'}), 404

    card = dict(row)
    updated = vocabulary.sm2_update(card, quality)

    db.execute(
        """UPDATE vocabulary SET repetitions=?, interval=?, easiness=?, next_review=?
           WHERE id=?""",
        (updated['repetitions'], updated['interval'],
         updated['easiness'], updated['next_review'], card_id)
    )
    db.commit()
    progress.log_activity('vocabulary', 1, 1 if quality >= 4 else 0)

    return jsonify({'success': True})


@app.route('/api/vocabulary/quiz')
def api_vocab_quiz():
    due = vocabulary.load_due_cards(limit=20)
    new = vocabulary.load_new_cards(limit=5)
    combined = due + new

    if not combined:
        return jsonify({'card': None, 'remaining': 0, 'total': 0})

    card = combined[0]
    remaining = len(combined) - 1

    db = get_db()
    distractors = db.execute(
        "SELECT definition FROM vocabulary WHERE id != ? ORDER BY RANDOM() LIMIT 3",
        (card['id'],)
    ).fetchall()

    options = [card['definition']]
    options.extend(r['definition'] for r in distractors)
    random.shuffle(options)

    return jsonify({
        'card': {
            'id': card['id'],
            'word': card['word'],
            'example': card['example'],
        },
        'correct_definition': card['definition'],
        'options': options,
        'remaining': remaining,
        'total': len(combined),
    })


# ─── Vocabulary Add ───────────────────────────────────────────────────────────

@app.route('/api/vocabulary/add', methods=['POST'])
def api_vocab_add():
    data = request.get_json()
    word = data.get('word', '').strip()
    if not word:
        return jsonify({'error': 'Word is required'}), 400

    db = get_db()
    db.execute(
        """INSERT INTO vocabulary (word, definition, example, synonyms, register, deck)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (word, data.get('definition', ''), data.get('example', ''),
         data.get('synonyms', ''), data.get('register', 'neutral'), 'c1_core')
    )
    db.commit()
    return jsonify({'success': True, 'id': db.lastrowid})


# ─── Grammar API ──────────────────────────────────────────────────────────────


@app.route('/api/grammar/structures')
def api_grammar_structures():
    return jsonify(grammar.STRUCTURE_DESCRIPTIONS)

@app.route('/api/grammar/generate')
def api_grammar_generate():
    db = get_db()
    rows = db.execute(
        """SELECT structure, SUM(correct) as c, COUNT(*) as total
           FROM grammar_log GROUP BY structure"""
    ).fetchall()

    weak = [r['structure'] for r in rows if r['c'] / r['total'] < 0.6] if rows else []
    pool = weak if weak else grammar.STRUCTURES
    structure = random.choice(pool)

    exercise = grammar.generate_exercise(structure)

    if 'error' in exercise:
        return jsonify({'error': 'Failed to generate exercise'}), 500

    return jsonify({
        'structure': structure,
        'instruction': exercise.get('instruction', ''),
        'question': exercise.get('question', ''),
        'answer': exercise.get('answer', ''),
        'explanation': exercise.get('explanation', ''),
        'tip': exercise.get('tip', ''),
    })


@app.route('/api/grammar/check', methods=['POST'])
def api_grammar_check():
    data = request.get_json()
    user_answer = data.get('answer', '').strip().lower()
    correct_answer = data.get('correct_answer', '').strip().lower()
    structure = data.get('structure', 'unknown')

    is_correct = user_answer == correct_answer or correct_answer in user_answer

    db = get_db()
    db.execute(
        "INSERT INTO grammar_log (structure, correct) VALUES (?, ?)",
        (structure, 1 if is_correct else 0)
    )
    db.commit()
    progress.log_activity('grammar', 1, 1 if is_correct else 0)

    return jsonify({'correct': is_correct})


# ─── Use of English API ───────────────────────────────────────────────────────

@app.route('/api/use-of-english/generate')
def api_uoe_generate():
    part = request.args.get('part', '4')
    if part not in use_of_english.PARTS:
        part = '4'
    exercise = use_of_english.generate_exercise(part)

    if 'error' in exercise:
        return jsonify({'error': 'Failed to generate exercise'}), 500

    return jsonify({'part': part, 'exercise': exercise})


# ─── Dashboard API ────────────────────────────────────────────────────────────

@app.route('/api/dashboard')
def api_dashboard():
    return jsonify({
        'streak': progress.get_streak(),
        'weekly': {k: dict(v) for k, v in progress.get_weekly_stats().items()},
        'vocab': progress.get_vocab_stats(),
        'weak_grammar': [dict(r) for r in progress.get_weak_grammar_structures()],
    })


# ─── Writing API ──────────────────────────────────────────────────────────────

WRITING_DIR = os.path.join(os.path.dirname(__file__), 'data', 'progress')

@app.route('/api/writing/prompts')
def api_writing_prompts():
    types = []
    for k, (name, key) in writing.TASK_TYPES.items():
        types.append({'id': k, 'name': name, 'key': key, 'prompt': writing.get_task_prompt(key)})
    return jsonify(types)


@app.route('/api/writing/submit', methods=['POST'])
def api_writing_submit():
    data = request.get_json()
    text = data.get('text', '').strip()
    task_type = data.get('task_type', 'essay')
    task_name = data.get('task_name', 'Essay')

    if len(text.split()) < 20:
        return jsonify({'error': 'Text too short (min 20 words)'}), 400

    feedback = writing.assess_writing(text, task_name)

    if 'raw_feedback' in feedback:
        return jsonify({'error': 'Failed to assess writing', 'raw': feedback['raw_feedback']}), 500

    os.makedirs(WRITING_DIR, exist_ok=True)
    filename = f"writing_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(os.path.join(WRITING_DIR, filename), 'w', encoding='utf-8') as f:
        json.dump({'text': text, 'feedback': feedback, 'task': task_name}, f, ensure_ascii=False)

    progress.log_activity('writing', 1, 1 if feedback.get('total', 0) >= 12 else 0)

    return jsonify(feedback)


@app.route('/api/writing/history')
def api_writing_history():
    os.makedirs(WRITING_DIR, exist_ok=True)
    files = []
    for fname in sorted(os.listdir(WRITING_DIR), reverse=True)[:20]:
        if fname.endswith('.json'):
            path = os.path.join(WRITING_DIR, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                files.append({
                    'file': fname,
                    'date': fname.replace('writing_', '').replace('.json', ''),
                    'task': data.get('task', ''),
                    'total': data.get('feedback', {}).get('total', 0),
                    'word_count': data.get('feedback', {}).get('word_count', 0),
                })
            except Exception:
                pass
    return jsonify(files)


@app.route('/api/writing/history/<filename>')
def api_writing_detail(filename):
    path = os.path.join(WRITING_DIR, filename)
    if not os.path.exists(path):
        return jsonify({'error': 'Not found'}), 404
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)


# ─── Frontend ─────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
