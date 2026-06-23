/* ═══════════════════════════════════════════════════════════════════════════
   C1 Advanced Trainer — Frontend Application
   ═══════════════════════════════════════════════════════════════════════════ */

(function() {
  'use strict';

  // ─── State ────────────────────────────────────────────────────────────────

  const state = {
    currentCard: null,
    totalCards: 0,
    reviewedCards: 0,
    remainingCards: 0,
    isFlipped: false,
    grammarExercise: null,
    grammarChecked: false,
    uoeExercise: null,
    uoePart: null,
    uoeChecked: false,
    uoeUserAnswers: [],
    writingTaskId: null,
    writingTaskKey: null,
    writingTaskName: null,
    writingHistory: [],
  };

  // ─── Helpers ──────────────────────────────────────────────────────────────

  async function api(url, options = {}) {
    try {
      const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        return { error: err.error || res.statusText };
      }
      return await res.json();
    } catch (err) {
      console.error('API error:', err);
      return { error: err.message };
    }
  }

  const $ = (id) => document.getElementById(id);

  function show(el) { if (el) el.classList.remove('hidden', 'd-none'); }
  function hide(el) { if (el) el.classList.add('hidden', 'd-none'); }

  // ─── Tab Switching ────────────────────────────────────────────────────────

  const tabBtns = document.querySelectorAll('.tab-btn');
  const sections = {
    vocabulary: $('tab-vocabulary'),
    grammar: $('tab-grammar'),
    uoe: $('tab-uoe'),
    writing: $('tab-writing'),
    dashboard: $('tab-dashboard'),
  };

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      Object.values(sections).forEach(s => s && s.classList.remove('active'));
      const sec = sections[tab];
      if (sec) sec.classList.add('active');
      if (tab === 'dashboard') loadDashboard();
      if (tab === 'grammar') loadCheatsheet();
      if (tab === 'writing') loadWritingHistory();
    });
  });

  // ─── Dark Mode ────────────────────────────────────────────────────────────

  const darkToggle = $('dark-toggle');
  if (localStorage.getItem('dark') === '1') {
    document.body.classList.add('dark');
  }

  darkToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    localStorage.setItem('dark', document.body.classList.contains('dark') ? '1' : '0');
  });

  // ─── ═══════════════════ VOCABULARY ═══════════════════ ──────────────────

  const flashcard = $('flashcard');
  const cardWord = $('card-word');
  const cardExample = $('card-example');
  const cardDefinition = $('card-definition');
  const cardSynonyms = $('card-synonyms');
  const cardRegister = $('card-register');
  const flipHint = $('flip-hint');
  const ratingGroup = $('rating-group');
  const progressFill = $('progress-fill');
  const progressLabel = $('progress-label');
  const vocabEmpty = $('vocab-empty');

  async function loadNextCard() {
    state.isFlipped = false;
    flashcard.classList.remove('flipped');
    ratingGroup.classList.remove('visible');
    if (vocabEmpty) vocabEmpty.classList.remove('visible');
    flashcard.style.display = '';

    const data = await api('/api/vocabulary/next');

    if (!data.card) {
      if (vocabEmpty) vocabEmpty.classList.add('visible');
      flashcard.style.display = 'none';
      ratingGroup.classList.remove('visible');
      if (flipHint) flipHint.classList.add('hidden');
      if (progressLabel) progressLabel.textContent = 'All done!';
      if (progressFill) progressFill.style.width = '100%';
      return;
    }

    if (flipHint) flipHint.classList.remove('hidden');

    state.currentCard = data.card;
    state.totalCards = data.total || 1;
    state.remainingCards = data.remaining || 0;
    state.reviewedCards = data.reviewed || 0;

    cardWord.textContent = data.card.word;
    cardExample.textContent = data.card.example || '';
    cardDefinition.textContent = data.card.definition;
    cardSynonyms.textContent = data.card.synonyms || '\u2014';
    cardRegister.textContent = data.card.register || 'neutral';

    updateProgress();
  }

  function updateProgress() {
    const done = state.totalCards - state.remainingCards;
    const pct = state.totalCards > 0 ? (done / state.totalCards) * 100 : 0;
    if (progressFill) progressFill.style.width = Math.min(pct, 100) + '%';
    if (progressLabel) progressLabel.textContent = `${done} / ${state.totalCards}`;
  }

  window.flipCard = function() {
    if (!state.currentCard) return;
    state.isFlipped = !state.isFlipped;
    flashcard.classList.toggle('flipped', state.isFlipped);
    if (state.isFlipped) {
      if (flipHint) flipHint.classList.add('hidden');
      ratingGroup.classList.add('visible');
    } else {
      ratingGroup.classList.remove('visible');
    }
  };

  async function rateCard(quality) {
    if (!state.currentCard || !state.isFlipped) return;
    await api('/api/vocabulary/review', {
      method: 'POST',
      body: JSON.stringify({ card_id: state.currentCard.id, quality }),
    });
    state.reviewedCards++;
    await loadNextCard();
  }

  document.querySelectorAll('.rating-btn').forEach(btn => {
    btn.addEventListener('click', () => rateCard(parseInt(btn.dataset.quality)));
  });

  // Keyboard shortcuts: 1=Again, 2=Hard, 3=Good, 4=Easy
  document.addEventListener('keydown', (e) => {
    if (!['1', '2', '3', '4'].includes(e.key)) return;
    const vocab = $('tab-vocabulary');
    if (!vocab || !vocab.classList.contains('active')) return;
    if (!state.isFlipped) return;
    const map = { '1': 0, '2': 3, '3': 4, '4': 5 };
    rateCard(map[e.key]);
  });

  // ─── Vocab Add ────────────────────────────────────────────────────────────

  window.addVocabCard = async function() {
    const word = $('v-word');
    const def = $('v-def');
    const example = $('v-example');
    const syns = $('v-synonyms');
    const register = $('v-register');
    const status = $('add-status');

    if (!word.value.trim()) {
      status.textContent = 'Word is required';
      status.style.color = 'var(--red)';
      return;
    }

    const res = await api('/api/vocabulary/add', {
      method: 'POST',
      body: JSON.stringify({
        word: word.value.trim(),
        definition: def.value.trim(),
        example: example.value.trim(),
        synonyms: syns.value.trim(),
        register: register.value,
      }),
    });

    if (res.success) {
      status.textContent = `\u2705 Added "${word.value.trim()}"`;
      status.style.color = 'var(--green)';
      word.value = ''; def.value = ''; example.value = ''; syns.value = '';
      loadNextCard();
    } else {
      status.textContent = `\u274c ${res.error}`;
      status.style.color = 'var(--red)';
    }
  };

  // ─── ═══════════════════ GRAMMAR ═══════════════════ ────────────────────

  const grammarStart = $('grammar-start');
  const grammarExercise = $('grammar-exercise');
  const grammarLoading = $('grammar-loading');
  const grammarStructure = $('grammar-structure');
  const grammarInstruction = $('grammar-instruction');
  const grammarQuestion = $('grammar-question');
  const grammarAnswer = $('grammar-answer');
  const grammarFeedback = $('grammar-feedback');
  const grammarResult = $('grammar-result');
  const grammarExplanation = $('grammar-explanation');
  const grammarTip = $('grammar-tip');
  const cheatsheetBody = $('cheatsheet-body');

  async function loadCheatsheet() {
    if (!cheatsheetBody || cheatsheetBody.dataset.loaded) return;
    const data = await api('/api/grammar/structures');
    cheatsheetBody.innerHTML = '';
    Object.entries(data).forEach(([key, desc]) => {
      const div = document.createElement('div');
      div.className = 'cheat-item';
      div.innerHTML = `<div class="cheat-name">${key.replace(/_/g, ' ')}</div>
        <div class="cheat-desc">${desc}</div>`;
      cheatsheetBody.appendChild(div);
    });
    cheatsheetBody.dataset.loaded = '1';
  }

  window.generateGrammar = async function() {
    state.grammarChecked = false;
    if (grammarStart) grammarStart.classList.add('hidden');
    if (grammarExercise) grammarExercise.classList.add('hidden');
    if (grammarFeedback) grammarFeedback.classList.add('hidden');
    if (grammarLoading) grammarLoading.classList.remove('hidden');
    if (grammarAnswer) { grammarAnswer.value = ''; grammarAnswer.disabled = true; }

    const data = await api('/api/grammar/generate');

    if (grammarLoading) grammarLoading.classList.add('hidden');

    if (data.error) {
      if (grammarStart) {
        grammarStart.classList.remove('hidden');
        grammarStart.querySelector('p').textContent =
          '\u26a0\ufe0f Error: Make sure your ANTHROPIC_API_KEY is set.';
      }
      return;
    }

    state.grammarExercise = data;
    if (grammarStructure) grammarStructure.textContent = data.structure.replace(/_/g, ' ');
    if (grammarInstruction) grammarInstruction.textContent = data.instruction;
    if (grammarQuestion) grammarQuestion.textContent = data.question;
    if (grammarExercise) grammarExercise.classList.remove('hidden');
    if (grammarAnswer) { grammarAnswer.disabled = false; grammarAnswer.focus(); }
  };

  window.checkGrammar = async function() {
    if (state.grammarChecked || !state.grammarExercise) return;
    const userAnswer = grammarAnswer ? grammarAnswer.value.trim() : '';
    if (!userAnswer) return;

    state.grammarChecked = true;
    if (grammarAnswer) grammarAnswer.disabled = true;

    await api('/api/grammar/check', {
      method: 'POST',
      body: JSON.stringify({
        answer: userAnswer,
        correct_answer: state.grammarExercise.answer,
        structure: state.grammarExercise.structure,
      }),
    });

    if (grammarFeedback) {
      grammarFeedback.classList.remove('hidden', 'correct', 'incorrect');
      const isCorrect = userAnswer.toLowerCase() === state.grammarExercise.answer.toLowerCase() ||
        state.grammarExercise.answer.toLowerCase().includes(userAnswer.toLowerCase());
      grammarFeedback.classList.add(isCorrect ? 'correct' : 'incorrect');
      if (grammarResult) {
        grammarResult.textContent = isCorrect
          ? '\u2705 Correct!'
          : `\u274c The answer was: ${state.grammarExercise.answer}`;
      }
    }

    if (grammarExplanation) grammarExplanation.textContent = state.grammarExercise.explanation;
    if (grammarTip) grammarTip.textContent = `\uD83D\uDCA1 Tip: ${state.grammarExercise.tip}`;
  };

  if (grammarAnswer) {
    grammarAnswer.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') checkGrammar();
    });
  }

  // ─── ═══════════════════ USE OF ENGLISH ═══════════════════ ────────────

  const uoeStart = $('uoe-start');
  const uoeLoading = $('uoe-loading');
  const uoeExerciseEl = $('uoe-exercise');
  const uoePartBadge = $('uoe-part-badge');
  const uoeBody = $('uoe-body');
  const uoeCheckBtn = $('uoe-check-btn');
  const uoeFeedback = $('uoe-feedback');
  const uoeNextBtn = $('uoe-next-btn');

  function showUoEStart() {
    state.uoeChecked = false;
    if (uoeStart) uoeStart.classList.remove('hidden');
    if (uoeExerciseEl) uoeExerciseEl.classList.add('hidden');
    if (uoeLoading) uoeLoading.classList.add('hidden');
    if (uoeFeedback) uoeFeedback.classList.add('hidden');
    if (uoeNextBtn) uoeNextBtn.classList.add('hidden');
  }
  window.showUoEStart = showUoEStart;

  document.querySelectorAll('.part-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const part = btn.dataset.part;
      state.uoePart = part;
      state.uoeChecked = false;

      if (uoeStart) uoeStart.classList.add('hidden');
      if (uoeExerciseEl) uoeExerciseEl.classList.add('hidden');
      if (uoeFeedback) uoeFeedback.classList.add('hidden');
      if (uoeNextBtn) uoeNextBtn.classList.add('hidden');
      if (uoeLoading) uoeLoading.classList.remove('hidden');

      const data = await api(`/api/use-of-english/generate?part=${part}`);
      if (uoeLoading) uoeLoading.classList.add('hidden');

      if (data.error) {
        if (uoeStart) {
          uoeStart.classList.remove('hidden');
          uoeStart.querySelector('p').textContent =
            '\u26a0\ufe0f Error: Make sure your ANTHROPIC_API_KEY is set.';
        }
        return;
      }

      state.uoeExercise = data.exercise;
      if (uoePartBadge) uoePartBadge.textContent = `Part ${part}: ${getPartName(part)}`;
      renderUoEExercise(part, data.exercise);
      if (uoeExerciseEl) uoeExerciseEl.classList.remove('hidden');
    });
  });

  function getPartName(part) {
    const names = { 1: 'Multiple-choice cloze', 2: 'Open cloze', 3: 'Word formation', 4: 'Key word transformation' };
    return names[part] || '';
  }

  function renderUoEExercise(part, ex) {
    if (uoeBody) uoeBody.innerHTML = '';
    if (uoeFeedback) uoeFeedback.classList.add('hidden');
    if (uoeCheckBtn) uoeCheckBtn.classList.remove('hidden');
    if (uoeNextBtn) uoeNextBtn.classList.add('hidden');
    state.uoeUserAnswers = [];
    state.uoeChecked = false;

    if (part === '1') renderPart1(ex);
    else if (part === '2') renderPart2or3(ex, 'answers');
    else if (part === '3') renderPart2or3(ex, 'sentences');
    else if (part === '4') renderPart4(ex);
  }

  function renderPart1(ex) {
    const text = document.createElement('p');
    text.className = 'exercise-question';
    text.textContent = ex.text || '';
    if (uoeBody) uoeBody.appendChild(text);

    (ex.questions || []).forEach((q, i) => {
      const div = document.createElement('div');
      div.className = 'uoe-gap';
      div.innerHTML = `<span class="gap-number">(${q.gap})</span>`;
      const optDiv = document.createElement('div');
      optDiv.className = 'uoe-options';
      optDiv.dataset.gapIndex = i;
      Object.entries(q.options).forEach(([letter, word]) => {
        const btn = document.createElement('button');
        btn.textContent = `${letter}) ${word}`;
        btn.dataset.letter = letter;
        btn.addEventListener('click', () => {
          if (state.uoeChecked) return;
          optDiv.querySelectorAll('button').forEach(b => b.classList.remove('selected'));
          btn.classList.add('selected');
          state.uoeUserAnswers[i] = letter;
        });
        optDiv.appendChild(btn);
      });
      div.appendChild(optDiv);
      if (uoeBody) uoeBody.appendChild(div);
    });
  }

  function renderPart2or3(ex, key) {
    const items = ex[key] || [];
    items.forEach((item, i) => {
      const div = document.createElement('div');
      div.className = 'uoe-gap';
      if (key === 'sentences') {
        const p = document.createElement('p');
        p.className = 'gap-context';
        p.textContent = item.sentence || '';
        div.appendChild(p);
        const root = document.createElement('p');
        root.style.cssText = 'font-size:13px;color:var(--text-muted);margin-bottom:6px;';
        root.textContent = `Root word: ${item.root || ''}`;
        div.appendChild(root);
      }
      const input = document.createElement('input');
      input.type = 'text';
      input.placeholder = 'Your answer...';
      input.autocomplete = 'off';
      input.dataset.gapIndex = i;
      input.dataset.expected = (item.answer || '').toLowerCase();
      input.addEventListener('keydown', (e) => { if (e.key === 'Enter') checkUoE(); });
      div.appendChild(input);
      if (uoeBody) uoeBody.appendChild(div);
    });
  }

  function renderPart4(ex) {
    const items = ex.items || [];
    items.forEach((item, i) => {
      const div = document.createElement('div');
      div.className = 'uoe-gap';
      div.innerHTML = `
        <p class="gap-context"><strong>Original:</strong> ${item.sentence || ''}</p>
        <p class="gap-context"><strong>Keyword:</strong> ${(item.keyword || '').toUpperCase()}</p>
        <p class="gap-context"><strong>Complete:</strong> ${item.incomplete || ''}</p>`;
      const input = document.createElement('input');
      input.type = 'text';
      input.placeholder = '3-6 words including the keyword...';
      input.autocomplete = 'off';
      input.dataset.gapIndex = i;
      input.dataset.expected = (item.answer || '').toLowerCase();
      input.addEventListener('keydown', (e) => { if (e.key === 'Enter') checkUoE(); });
      div.appendChild(input);
      if (uoeBody) uoeBody.appendChild(div);
    });
  }

  window.checkUoE = function() {
    if (state.uoeChecked || !state.uoeExercise) return;
    state.uoeChecked = true;

    const part = state.uoePart;
    let correctCount = 0;
    let totalCount = 0;

    if (part === '1') {
      const groups = uoeBody ? uoeBody.querySelectorAll('.uoe-options') : [];
      const questions = state.uoeExercise.questions || [];
      groups.forEach((group, i) => {
        const btns = group.querySelectorAll('button');
        const q = questions[i];
        if (!q) return;
        totalCount++;
        btns.forEach(b => {
          b.style.pointerEvents = 'none';
          if (b.dataset.letter === q.answer) b.classList.add('correct');
          else if (b.classList.contains('selected')) b.classList.add('wrong');
        });
        const selected = group.querySelector('.selected');
        if (selected && selected.dataset.letter === q.answer) correctCount++;
      });
    } else {
      const inputs = uoeBody ? uoeBody.querySelectorAll('input') : [];
      inputs.forEach(input => {
        input.disabled = true;
        totalCount++;
        const userAns = input.value.trim().toLowerCase();
        const expected = input.dataset.expected;
        const isCorrect = userAns === expected || expected.includes(userAns) || userAns.includes(expected);
        if (isCorrect) { input.classList.add('correct'); correctCount++; }
        else {
          input.classList.add('incorrect');
          const hint = document.createElement('p');
          hint.style.cssText = 'font-size:13px;color:var(--red);margin-top:4px;';
          hint.textContent = `Answer: ${expected}`;
          input.parentNode.appendChild(hint);
        }
      });
    }

    if (uoeCheckBtn) uoeCheckBtn.classList.add('hidden');
    if (uoeFeedback) {
      uoeFeedback.classList.remove('hidden', 'correct', 'incorrect');
      uoeFeedback.classList.add(correctCount === totalCount ? 'correct' : 'incorrect');
      uoeFeedback.innerHTML = `<p class="feedback-result">${
        correctCount === totalCount ? '\u2705 Perfect!' : `\uD83D\uDCCA ${correctCount}/${totalCount} correct`
      }</p>`;
    }

    if (part === '4' && state.uoeExercise.items) {
      let html = '';
      state.uoeExercise.items.forEach((item, i) => {
        if (item.explanation) {
          html += `<p style="font-size:14px;color:var(--text-secondary);margin-bottom:4px;margin-top:8px;">
            <strong>Item ${i+1}:</strong> ${item.explanation}</p>`;
        }
      });
      if (uoeFeedback) uoeFeedback.innerHTML += html;
    }

    if (uoeNextBtn) uoeNextBtn.classList.remove('hidden');
  };

  // ─── ═══════════════════ WRITING ═══════════════════ ────────────────────

  const writingTaskSelect = $('writing-task-select');
  const writingTaskList = $('writing-task-list');
  const writingEditor = $('writing-editor');
  const writingTaskName = $('writing-task-name');
  const writingPromptText = $('writing-prompt-text');
  const writingText = $('writing-text');
  const writingWordcount = $('writing-wordcount');
  const writingSubmitBtn = $('writing-submit-btn');
  const writingLoading = $('writing-loading');
  const writingFeedback = $('writing-feedback');
  const writingGradeBadge = $('writing-grade-badge');
  const writingScore = $('writing-score');
  const writingScores = $('writing-scores');
  const writingStrengths = $('writing-strengths');
  const writingImprovements = $('writing-improvements');
  const writingCorrections = $('writing-corrections');
  const writingVocabUpgrades = $('writing-vocab-upgrades');
  const writingModelOpening = $('writing-model-opening');
  const writingHistoryList = $('writing-history-list');

  let selectedTask = null;

  async function loadWritingPrompts() {
    const data = await api('/api/writing/prompts');
    if (data.error) return;
    if (!writingTaskList) return;
    writingTaskList.innerHTML = '';
    data.forEach(t => {
      const btn = document.createElement('button');
      btn.className = 'writing-task-btn';
      btn.innerHTML = `${t.name} <small>${t.prompt.substring(0, 80)}...</small>`;
      btn.addEventListener('click', () => selectWritingTask(t, btn));
      writingTaskList.appendChild(btn);
    });
  }

  function selectWritingTask(task, btn) {
    selectedTask = task;
    if (writingTaskSelect) writingTaskSelect.classList.add('hidden');
    if (writingEditor) writingEditor.classList.remove('hidden');
    if (writingFeedback) writingFeedback.classList.add('hidden');
    if (writingTaskName) writingTaskName.textContent = task.name;
    if (writingPromptText) writingPromptText.textContent = task.prompt;
    if (writingText) { writingText.value = ''; writingText.focus(); }
    updateWordCount();
  }

  function updateWordCount() {
    if (!writingText || !writingWordcount) return;
    const count = writingText.value.trim() ? writingText.value.trim().split(/\s+/).length : 0;
    writingWordcount.textContent = count;
  }

  if (writingText) {
    writingText.addEventListener('input', updateWordCount);
    writingText.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = writingText.selectionStart;
        writingText.value = writingText.value.substring(0, start) + '  ' + writingText.value.substring(writingText.selectionEnd);
        writingText.selectionStart = writingText.selectionEnd = start + 2;
      }
    });
  }

  let activeWritingFilename = null;

  window.submitWriting = async function() {
    if (!writingText || !selectedTask) return;
    const text = writingText.value.trim();
    if (!text || text.split(/\s+/).length < 20) {
      alert('Please write at least 20 words.');
      return;
    }

    if (writingEditor) writingEditor.classList.add('hidden');
    if (writingFeedback) writingFeedback.classList.add('hidden');
    if (writingLoading) writingLoading.classList.remove('hidden');
    if (writingSubmitBtn) writingSubmitBtn.disabled = true;

    const data = await api('/api/writing/submit', {
      method: 'POST',
      body: JSON.stringify({
        text,
        task_type: selectedTask.key,
        task_name: selectedTask.name,
      }),
    });

    if (writingLoading) writingLoading.classList.add('hidden');
    if (writingSubmitBtn) writingSubmitBtn.disabled = false;

    if (data.error) {
      if (writingEditor) writingEditor.classList.remove('hidden');
      alert(data.error);
      return;
    }

    displayWritingFeedback(data);
    loadWritingHistory();
  };

  function displayWritingFeedback(fb) {
    if (writingFeedback) writingFeedback.classList.remove('hidden');
    if (writingEditor) writingEditor.classList.add('hidden');
    if (writingGradeBadge) {
      writingGradeBadge.textContent = `Grade: ${fb.cae_grade || 'N/A'}`;
    }
    if (writingScore) {
      writingScore.textContent = `${fb.total || 0}/20`;
      writingScore.style.color = (fb.total || 0) >= 12 ? 'var(--green)' : 'var(--red)';
    }

    // Scores
    if (writingScores) {
      writingScores.innerHTML = '<h4 style="font-size:14px;font-weight:600;color:var(--text-secondary);margin-bottom:8px;">Criteria Scores</h4>';
      const criteria = ['content', 'communicative_achievement', 'organisation', 'language'];
      const labels = {
        content: 'Content',
        communicative_achievement: 'Comm. Achievement',
        organisation: 'Organisation',
        language: 'Language',
      };
      const scores = fb.scores || {};
      criteria.forEach(c => {
        const s = scores[c] || { score: 0, comment: '' };
        const pct = (s.score / 5) * 100;
        const colors = ['#ef4444', '#ef4444', '#f59e0b', '#22c55e', '#22c55e', '#6366f1'];
        const row = document.createElement('div');
        row.className = 'writing-score-row';
        row.innerHTML = `
          <span class="writing-score-label">${labels[c]}</span>
          <div class="writing-score-bar">
            <div class="writing-score-fill" style="width:${pct}%;background:${colors[s.score] || '#6366f1'}"></div>
          </div>
          <span class="writing-score-num">${s.score}/5</span>
        `;
        writingScores.appendChild(row);
        if (s.comment) {
          const comment = document.createElement('p');
          comment.style.cssText = 'font-size:13px;color:var(--text-muted);margin:-4px 0 8px;';
          comment.textContent = s.comment;
          writingScores.appendChild(comment);
        }
      });
    }

    // Strengths
    if (writingStrengths) {
      const items = fb.strengths || [];
      writingStrengths.innerHTML = items.length
        ? `<div class="writing-subsection"><h4>\u2705 Strengths</h4><ul>${
            items.map(s => `<li>${s}</li>`).join('')
          }</ul></div>`
        : '';
    }

    // Improvements
    if (writingImprovements) {
      const items = fb.improvements || [];
      writingImprovements.innerHTML = items.length
        ? `<div class="writing-subsection"><h4>\uD83C\uDFAF Areas to Improve</h4><ul>${
            items.map(s => `<li>${s}</li>`).join('')
          }</ul></div>`
        : '';
    }

    // Corrections
    if (writingCorrections) {
      const corrections = fb.corrected_sentences || [];
      writingCorrections.innerHTML = corrections.length
        ? `<div class="writing-subsection"><h4>\uD83D\uDD27 Language Corrections</h4>${
            corrections.slice(0, 5).map(c => `
              <div class="writing-correction">
                <div class="orig">${c.original || ''}</div>
                <div class="corr">${c.corrected || ''}</div>
                <div class="reason">${c.explanation || ''}</div>
              </div>
            `).join('')
          }</div>`
        : '';
    }

    // Vocab upgrades
    if (writingVocabUpgrades) {
      const items = fb.c1_vocabulary_suggestions || [];
      writingVocabUpgrades.innerHTML = items.length
        ? `<div class="writing-subsection"><h4>\uD83D\uDCC8 Vocabulary Upgrades</h4><ul>${
            items.slice(0, 5).map(s => `<li>${s}</li>`).join('')
          }</ul></div>`
        : '';
    }

    // Model opening
    if (writingModelOpening) {
      const model = fb.model_opening || '';
      writingModelOpening.innerHTML = model
        ? `<strong>\uD83D\uDCDD Model Opening</strong><br>${model}`
        : '';
    }

    if (writingFeedback) writingFeedback.classList.remove('hidden');
  }

  async function loadWritingHistory() {
    const data = await api('/api/writing/history');
    if (data.error || !writingHistoryList) return;
    state.writingHistory = data;
    if (data.length === 0) {
      writingHistoryList.innerHTML = '<p class="empty-dashboard">No submissions yet.</p>';
      return;
    }
    writingHistoryList.innerHTML = data.map(item => `
      <div class="writing-history-item" onclick="viewWritingDetail('${item.file}')">
        <div>
          <div class="history-task">${item.task || 'Writing'}</div>
          <div class="history-date">${item.date || ''}</div>
        </div>
        <div class="history-score ${(item.total || 0) >= 12 ? 'pass' : 'fail'}">
          ${item.total || 0}/20
        </div>
      </div>
    `).join('');
    writingHistoryList.dataset.loaded = '1';
  }

  window.viewWritingDetail = async function(filename) {
    const data = await api(`/api/writing/history/${filename}`);
    if (data.error) return;
    selectedTask = { key: data.task || 'essay', name: data.task || 'Writing' };
    displayWritingFeedback(data.feedback || {});
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ─── ═══════════════════ DASHBOARD ═══════════════════ ──────────────────

  async function loadDashboard() {
    const data = await api('/api/dashboard');
    if (data.error) return;

    const setStat = (id, val) => {
      const el = document.querySelector(`#${id} .stat-value`);
      if (el) el.textContent = val;
    };

    setStat('stat-streak', data.streak || 0);

    if (data.vocab) {
      setStat('stat-total-cards', data.vocab.total || 0);
      const pct = data.vocab.total > 0 ? Math.round((data.vocab.mature / data.vocab.total) * 100) : 0;
      setStat('stat-mature', pct + '%');
      setStat('stat-due', data.vocab.due_today || 0);
    }

    // Weekly chart
    renderWeeklyChart(data.weekly || {});

    // Weekly stats
    const weeklyContainer = $('weekly-stats');
    const weekly = data.weekly || {};
    const labels = { vocabulary: 'Vocabulary', grammar: 'Grammar', writing: 'Writing', use_of_english: 'UoE' };

    if (weeklyContainer) {
      if (Object.keys(weekly).length === 0) {
        weeklyContainer.innerHTML = '<p class="empty-dashboard">No activity this week yet.</p>';
      } else {
        weeklyContainer.innerHTML = '';
        ['vocabulary', 'grammar', 'writing', 'use_of_english'].forEach(key => {
          if (!weekly[key]) return;
          const s = weekly[key];
          const acc = s.total_items > 0 ? Math.round((s.total_correct / s.total_items) * 100) : 0;
          const item = document.createElement('div');
          item.className = 'weekly-item';
          item.innerHTML = `
            <span class="weekly-label">${labels[key] || key}</span>
            <div class="weekly-bar"><div class="weekly-fill" style="width:${acc}%"></div></div>
            <span class="weekly-text">${s.total_correct}/${s.total_items} (${acc}%)</span>`;
          weeklyContainer.appendChild(item);
        });
      }
    }

    // Weak grammar
    const weakContainer = $('weak-grammar-list');
    const weak = data.weak_grammar || [];
    if (weakContainer) {
      if (weak.length === 0) {
        weakContainer.innerHTML = '<p class="empty-dashboard">No weak structures detected yet.</p>';
      } else {
        weakContainer.innerHTML = '';
        weak.forEach(s => {
          const pct = Math.round(s.accuracy * 100);
          const cls = pct < 40 ? 'low' : pct < 70 ? 'medium' : 'high';
          const item = document.createElement('div');
          item.className = 'weak-item';
          item.innerHTML = `
            <span class="weak-name">${s.structure.replace(/_/g, ' ')}</span>
            <span class="weak-accuracy ${cls}">${pct}% (${s.attempts} attempts)</span>`;
          weakContainer.appendChild(item);
        });
      }
    }

    // Exam readiness
    const readiness = $('exam-readiness');
    const vocab = data.vocab || {};
    const totalItems = Object.values(weekly).reduce((sum, s) => sum + (s.total_items || 0), 0);
    const vocabMaturity = vocab.total > 0 ? vocab.mature / vocab.total : 0;

    let level, color;
    if (totalItems < 30 || vocabMaturity < 0.2) {
      level = '\uD83D\uDD34 Early stage \u2014 keep building daily habits';
      color = '#ef4444';
    } else if (totalItems < 100 || vocabMaturity < 0.5) {
      level = '\uD83D\uDFE1 Progressing \u2014 focus on weak areas';
      color = '#f59e0b';
    } else {
      level = '\uD83D\uDFE2 On track \u2014 consider a mock exam soon';
      color = '#22c55e';
    }
    if (readiness) {
      readiness.innerHTML = `<p style="font-size:16px;color:${color};font-weight:600;">${level}</p>`;
    }
  }

  function renderWeeklyChart(weekly) {
    const chartEl = $('weekly-chart');
    if (!chartEl) return;
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    // Generate simulated daily data from the weekly aggregate
    const totalItems = Object.values(weekly).reduce((sum, s) => sum + (s.total_items || 0), 0);
    if (totalItems === 0) {
      chartEl.innerHTML = '';
      return;
    }
    // Distribute items across days for visual (weight recent days more)
    const dayValues = days.map((_, i) => {
      const weight = (i + 1) / 28; // 1+2+...+7 = 28
      return Math.round(totalItems * weight);
    });
    const maxVal = Math.max(...dayValues, 1);
    chartEl.innerHTML = dayValues.map((val, i) => `
      <div class="chart-bar" style="height:${(val / maxVal) * 80 + 4}%;background:linear-gradient(to top, var(--indigo), var(--purple))">
        <div class="chart-tooltip">${val} items</div>
        <div class="chart-label">${days[i]}</div>
      </div>
    `).join('');
  }

  // ─── Init ──────────────────────────────────────────────────────────────

  loadNextCard();
  loadWritingPrompts();

})();
