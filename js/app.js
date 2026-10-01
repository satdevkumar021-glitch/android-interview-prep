/**
 * Android Interview Mastery - Master Application Controller
 * Version: 3.2.0 (Senior & Staff Architect Edition)
 *
 * Core Features:
 * 1. SPA Navigation & Hash Routing (#topic-0 to #topic-10)
 * 2. 3D Interactive Flip Card System ("First ask question, then flip answer")
 * 3. Fullscreen Distraction-Free Flashcard Deck (Spacebar to flip, Arrow keys to step)
 * 4. Real-Time Dynamic Progress Tracking (0% -> 100% per topic badge in sidebar)
 * 5. Overall Curriculum Mastery Bar & Live Interview Readiness Score
 * 6. Recall Self-Evaluation ([ 😟 1 ] [ 😐 3 ] [ 🔥 5 ]) with auto-completion
 * 7. Debounced Global Search (Ctrl+K / ⌘K) across concepts, code, and 50 interview Q&As
 * 8. One-Click Syntax-Highlighted Code Copy Buttons
 * 9. Mobile Responsive Sidebar Drawer with Backdrop Lock
 * 10. Dark / Light Theme Toggle with LocalStorage persistence
 */

(() => {
  'use strict';

  // --- Constants & Storage Keys ---
  const STORAGE_KEYS = {
    PROGRESS: 'android-prep-progress-v3',
    RATINGS: 'android-prep-ratings-v3',
    THEME: 'android-prep-theme-v3'
  };

  let currentTopicId = '0';
  let progressData = {}; // { 'topicNum_itemIdx': boolean }
  let ratingData = {};   // { 'questionId': number }
  let activeDeck = [];
  let currentDeckIndex = 0;
  let isDeckCardFlipped = false;

  // Load Saved Data safely
  try {
    progressData = JSON.parse(localStorage.getItem(STORAGE_KEYS.PROGRESS) || '{}');
    ratingData = JSON.parse(localStorage.getItem(STORAGE_KEYS.RATINGS) || '{}');
  } catch (e) {
    progressData = {};
    ratingData = {};
  }

  // --- Utility Functions ---
  function clamp(val, min, max) {
    return Math.min(Math.max(val, min), max);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // --- 1. SPA Navigation & Hash Routing ---
  function navigateToTopic(topicId, updateHash = true, smoothScroll = true) {
    currentTopicId = String(topicId);

    // Toggle Active Section
    document.querySelectorAll('.topic-section').forEach(sec => {
      sec.classList.toggle('active', sec.id === `topic-${currentTopicId}`);
    });

    // Toggle Active Nav Link
    document.querySelectorAll('.nav-link[data-topic]').forEach(link => {
      const isActive = link.getAttribute('data-topic') === currentTopicId;
      link.classList.toggle('active', isActive);
      link.setAttribute('aria-current', isActive ? 'page' : 'false');
    });

    if (updateHash) {
      const hash = `#topic-${currentTopicId}`;
      if (window.location.hash !== hash) {
        window.history.pushState ? window.history.pushState(null, '', hash) : (window.location.hash = hash);
      }
    }

    if (smoothScroll) window.scrollTo({ top: 0, behavior: 'smooth' });
    toggleMobileSidebar(false);
    updateScrollProgress();
  }

  function handleHashNavigation() {
    const hash = window.location.hash || '';
    const match = hash.match(/^#topic-(\d+)$/);
    navigateToTopic(match ? match[1] : '0', false, Boolean(match));
  }

  function initNavigation() {
    document.querySelectorAll('.nav-link[data-topic]').forEach(link => {
      link.addEventListener('click', e => {
        e.preventDefault();
        const tid = link.getAttribute('data-topic');
        navigateToTopic(tid, true, true);
      });
    });

    // Quick filter in sidebar
    const filterInput = document.querySelector('.sidebar-filter-input');
    if (filterInput) {
      filterInput.addEventListener('input', e => {
        const query = e.target.value.toLowerCase().trim();
        document.querySelectorAll('.nav-link[data-topic]').forEach(link => {
          const text = link.textContent.toLowerCase();
          link.style.display = text.includes(query) ? 'flex' : 'none';
        });
      });
    }

    window.addEventListener('hashchange', handleHashNavigation);
    handleHashNavigation();
  }

  // --- 2. Progress Tracking (Per-Topic & Overall) ---
  function updateTopicProgress(topicNum) {
    // Select all inputs for this topic
    const checkboxes = Array.from(document.querySelectorAll(`input[type="checkbox"][data-topic="${topicNum}"]`));
    if (!checkboxes.length) return;

    const checkedCount = checkboxes.filter(c => c.checked).length;
    const pct = Math.round((checkedCount / checkboxes.length) * 100);

    // Update Sidebar Badge for this topic
    const badge = document.querySelector(`.topic-progress[data-topic-progress="${topicNum}"]`);
    if (badge) {
      badge.textContent = `${pct}%`;
      badge.classList.toggle('completed', pct === 100);
    }
  }

  function updateOverallMastery() {
    const allCheckboxes = Array.from(document.querySelectorAll('input[type="checkbox"][data-topic]'));
    if (!allCheckboxes.length) return;

    const totalChecked = allCheckboxes.filter(c => c.checked).length;
    const overallPct = Math.round((totalChecked / allCheckboxes.length) * 100);

    // Update Progress Bar in Sidebar
    document.querySelectorAll('.overall-progress').forEach(el => {
      el.style.width = `${overallPct}%`;
      if (el.classList.contains('progress-fill')) {
        el.textContent = `${overallPct}%`;
      }
    });

    // Update Progress Text
    const labelText = document.querySelector('.overall-progress-text');
    if (labelText) {
      labelText.textContent = `${overallPct}%`;
    }

    // Update Readiness Meter in Sidebar
    const readinessScoreEl = document.querySelector('.readiness-score');
    if (readinessScoreEl) {
      readinessScoreEl.textContent = `${overallPct}%`;
      readinessScoreEl.style.color = overallPct >= 80 ? 'var(--accent-green)' : overallPct >= 40 ? 'var(--accent-yellow)' : 'var(--accent-blue)';
    }
  }

  function initProgressTracking() {
    // Restore Saved Checkbox State using input[type="checkbox"][data-topic]
    document.querySelectorAll('input[type="checkbox"][data-topic]').forEach(cb => {
      const topic = cb.getAttribute('data-topic');
      const item = cb.getAttribute('data-item');
      const key = `${topic}_${item}`;

      if (progressData[key]) {
        cb.checked = true;
      }

      cb.addEventListener('change', () => {
        progressData[key] = cb.checked;
        try {
          localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify(progressData));
        } catch (e) {}

        updateTopicProgress(topic);
        updateOverallMastery();
      });
    });

    // Initialize progress for all 41 topics
    for (let t = 1; t <= 41; t++) {
      updateTopicProgress(t);
    }
    updateOverallMastery();
  }

  // --- 3. Interactive Question & Answer Flip System ---
  function extractQADataFromSection(sec) {
    const qaItems = sec.querySelectorAll('.qa-item');
    const questions = [];

    qaItems.forEach((item, idx) => {
      const qNumEl = item.querySelector('.qa-number');
      const qBadgeEl = item.querySelector('.badge');
      const qaQuestionEl = item.querySelector('.qa-question');
      const aTextEl = item.querySelector('.qa-answer');

      const qNum = qNumEl ? qNumEl.textContent.trim() : `Q${idx + 1}`;
      
      let diff = 'Senior';
      if (qBadgeEl && qBadgeEl.textContent.trim()) {
        diff = qBadgeEl.textContent.trim();
      } else if (item.getAttribute('data-difficulty')) {
        const raw = item.getAttribute('data-difficulty');
        diff = raw.charAt(0).toUpperCase() + raw.slice(1);
      }

      let question = '';
      if (qaQuestionEl) {
        const qClone = qaQuestionEl.cloneNode(true);
        const numInClone = qClone.querySelector('.qa-number');
        if (numInClone) numInClone.remove();
        const badgeInClone = qClone.querySelector('.badge');
        if (badgeInClone) badgeInClone.remove();
        question = qClone.innerHTML.trim();
      }

      const answer = aTextEl ? aTextEl.innerHTML.trim() : '';

      questions.push({
        id: `${sec.id}_q${idx + 1}`,
        number: qNum,
        difficulty: diff,
        question: question,
        answer: answer
      });
    });

    return questions;
  }

  function buildFlipCardElement(qData, topicNum) {
    const card = document.createElement('div');
    card.className = 'flip-card';
    card.id = `flip-${qData.id}`;
    card.setAttribute('data-id', qData.id);

    const savedRating = ratingData[qData.id] || 0;

    card.innerHTML = `
      <div class="flip-card-inner">
        <!-- FRONT: The Question -->
        <div class="flip-card-front">
          <div class="flip-card-header">
            <span class="badge ${qData.difficulty.toLowerCase().includes('scenario') ? 'badge-scenario' : qData.difficulty.toLowerCase().includes('advanced') ? 'badge-advanced' : 'badge-basic'}">
              ${qData.difficulty}
            </span>
            <span class="qa-number">${qData.number}</span>
          </div>

          <div class="flip-card-question">
            ${qData.question}
          </div>

          <div class="flip-card-prompt">
            <span>🤔</span>
            <em>Think about your answer, then flip to reveal!</em>
          </div>

          <div class="flip-card-footer">
            <span style="font-size:0.8rem; color:var(--text-muted);">Interactive Practice</span>
            <button type="button" class="flip-action-btn">
              <span>🔄 Flip to Answer</span>
            </button>
          </div>
        </div>

        <!-- BACK: The Principal Answer -->
        <div class="flip-card-back">
          <div class="flip-card-header">
            <span class="badge badge-scenario">🎓 Senior / Staff Answer</span>
            <span class="qa-number">${qData.number}</span>
          </div>

          <div class="flip-card-answer-content" style="flex:1; overflow-y:auto; padding-right:4px; font-size:0.92rem; line-height:1.65; color:var(--text-primary); margin:0.5rem 0;">
            ${qData.answer}
          </div>

          <!-- Self Rating Bar on Back -->
          <div class="self-rating-bar" style="margin-top:0.75rem; padding:0.5rem 0.75rem;">
            <span class="rating-label" style="font-size:0.75rem;">Rate Recall:</span>
            <div class="rating-buttons" data-qid="${qData.id}" data-topic="${topicNum}">
              <button type="button" class="rate-btn ${savedRating === 1 ? 'selected-1' : ''}" data-score="1" title="Need to review">😟 1</button>
              <button type="button" class="rate-btn ${savedRating === 3 ? 'selected-3' : ''}" data-score="3" title="Good grasp">😐 3</button>
              <button type="button" class="rate-btn ${savedRating === 5 ? 'selected-5' : ''}" data-score="5" title="Staff Mastered!">🔥 5</button>
            </div>
            <button type="button" class="flip-back-btn">🔄 Flip Back</button>
          </div>
        </div>
      </div>
    `;

    // Click handler for card flip (front click or button click)
    const frontEl = card.querySelector('.flip-card-front');
    const flipBtn = card.querySelector('.flip-action-btn');
    const flipBackBtn = card.querySelector('.flip-back-btn');

    const doFlip = (e) => {
      e.stopPropagation();
      card.classList.add('is-flipped');
    };

    const doUnflip = (e) => {
      e.stopPropagation();
      card.classList.remove('is-flipped');
    };

    if (frontEl) frontEl.addEventListener('click', doFlip);
    if (flipBtn) flipBtn.addEventListener('click', doFlip);
    if (flipBackBtn) flipBackBtn.addEventListener('click', doUnflip);

    // Rating handler
    card.querySelectorAll('.rate-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        const score = parseInt(btn.getAttribute('data-score'), 10);
        const qid = btn.parentElement.getAttribute('data-qid');
        const tnum = btn.parentElement.getAttribute('data-topic');

        ratingData[qid] = score;
        try {
          localStorage.setItem(STORAGE_KEYS.RATINGS, JSON.stringify(ratingData));
        } catch (err) {}

        btn.parentElement.querySelectorAll('.rate-btn').forEach(b => {
          b.classList.remove('selected-1', 'selected-3', 'selected-5');
        });
        btn.classList.add(`selected-${score}`);

        // If user scored 5 (Mastered), automatically check the 5th checklist item for that topic!
        if (score === 5 && tnum) {
          const chk = document.querySelector(`input[type="checkbox"][data-topic="${tnum}"][data-item="4"]`);
          if (chk && !chk.checked) {
            chk.checked = true;
            chk.dispatchEvent(new Event('change'));
          }
        }
      });
    });

    return card;
  }

  function enhanceAllQASections() {
    document.querySelectorAll('.topic-section').forEach(sec => {
      const qaSection = sec.querySelector('.qa-section');
      if (!qaSection) return;
      if (qaSection.querySelector('.qa-view-switcher')) return; // Avoid re-injection

      const topicNum = sec.id.replace('topic-', '');
      const questions = extractQADataFromSection(sec);
      if (!questions.length) return;

      // 1. Build View Switcher Toolbar
      const switcherBar = document.createElement('div');
      switcherBar.className = 'qa-view-switcher';
      switcherBar.innerHTML = `
        <button type="button" class="qa-view-btn active" data-view="cards">🎴 3D Flip Cards (Interactive)</button>
        <button type="button" class="qa-view-btn" data-view="accordion">📋 Accordion List</button>
        <button type="button" class="qa-view-btn deck-btn" style="margin-left:auto; background:rgba(168,85,247,0.15); border-color:var(--accent-purple); color:var(--accent-purple);">
          🎴 Launch Fullscreen Deck
        </button>
      `;

      // 2. Build 3D Flip Deck Grid
      const deckContainer = document.createElement('div');
      deckContainer.className = 'flip-deck-container';
      questions.forEach(q => {
        deckContainer.appendChild(buildFlipCardElement(q, topicNum));
      });

      // Insert switcher and deck before QA items
      const firstQAItem = qaSection.querySelector('.qa-item');
      if (firstQAItem) {
        qaSection.insertBefore(switcherBar, firstQAItem);
        qaSection.insertBefore(deckContainer, firstQAItem);
      }

      // Hide original accordion items by default (Flip Cards active by default)
      const accordionItems = qaSection.querySelectorAll('.qa-item');
      accordionItems.forEach(it => (it.style.display = 'none'));

      // Switcher Button Listeners
      const viewBtns = switcherBar.querySelectorAll('.qa-view-btn:not(.deck-btn)');
      viewBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          viewBtns.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');

          const viewMode = btn.getAttribute('data-view');
          if (viewMode === 'cards') {
            deckContainer.style.display = 'grid';
            accordionItems.forEach(it => (it.style.display = 'none'));
          } else {
            deckContainer.style.display = 'none';
            accordionItems.forEach(it => (it.style.display = ''));
          }
        });
      });

      // Launch Deck Modal Listener
      const deckLaunchBtn = switcherBar.querySelector('.deck-btn');
      if (deckLaunchBtn) {
        deckLaunchBtn.addEventListener('click', () => {
          const header = sec.querySelector('.topic-header h1');
          const title = header ? header.textContent.trim() : `Topic ${topicNum}`;
          openFullscreenDeck(questions, `${title} - Flashcard Deck`);
        });
      }
    });
  }

  // --- 4. Distraction-Free Fullscreen Flashcard Modal Deck ---
  function createFlashcardModalIfMissing() {
    if (document.querySelector('.flashcard-modal')) return;

    const modal = document.createElement('div');
    modal.className = 'flashcard-modal';
    modal.innerHTML = `
      <div class="flashcard-container">
        <div class="flashcard-close" title="Close (Esc)">&times;</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="badge badge-scenario deck-topic-title">Practice Deck</span>
          <span class="deck-counter" style="font-family:var(--font-mono); font-size:0.85rem; color:var(--text-muted);">1 / 5</span>
        </div>

        <div class="flashcard-box">
          <div class="flashcard-question-area"></div>
        </div>

        <div class="flashcard-hint">
          <span>💡 Tap card or press <strong>Spacebar</strong> to flip</span> &bull;
          <span>Press <strong>&larr; / &rarr;</strong> to navigate</span>
        </div>

        <div class="flashcard-controls">
          <button type="button" class="btn deck-prev-btn" style="background:var(--bg-secondary); border:1px solid var(--border-color); color:var(--text-primary); padding:0.5rem 1rem; border-radius:var(--radius-md); cursor:pointer;">&larr; Previous</button>
          <button type="button" class="btn deck-flip-btn" style="background:linear-gradient(135deg, var(--accent-purple), var(--accent-blue)); color:#fff; border:none; padding:0.6rem 1.25rem; border-radius:var(--radius-md); font-weight:700; cursor:pointer;">🔄 Flip Card</button>
          <button type="button" class="btn deck-next-btn" style="background:var(--bg-secondary); border:1px solid var(--border-color); color:var(--text-primary); padding:0.5rem 1rem; border-radius:var(--radius-md); cursor:pointer;">Next &rarr;</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Wire up events
    modal.querySelector('.flashcard-close').addEventListener('click', () => modal.classList.remove('active'));
    modal.querySelector('.deck-flip-btn').addEventListener('click', toggleDeckCardFlip);
    modal.querySelector('.flashcard-box').addEventListener('click', toggleDeckCardFlip);
    modal.querySelector('.deck-prev-btn').addEventListener('click', () => stepDeck(-1));
    modal.querySelector('.deck-next-btn').addEventListener('click', () => stepDeck(1));
  }

  function openFullscreenDeck(questions, title) {
    createFlashcardModalIfMissing();
    activeDeck = questions;
    currentDeckIndex = 0;
    isDeckCardFlipped = false;

    const modal = document.querySelector('.flashcard-modal');
    modal.querySelector('.deck-topic-title').textContent = title;
    modal.classList.add('active');

    renderCurrentDeckCard();
  }

  function renderCurrentDeckCard() {
    const modal = document.querySelector('.flashcard-modal');
    if (!modal || !activeDeck.length) return;

    const card = activeDeck[currentDeckIndex];
    const area = modal.querySelector('.flashcard-question-area');
    const counter = modal.querySelector('.deck-counter');

    counter.textContent = `${currentDeckIndex + 1} / ${activeDeck.length}`;

    if (!isDeckCardFlipped) {
      area.innerHTML = `
        <div style="font-size:0.8rem; text-transform:uppercase; color:var(--accent-purple); font-weight:700; margin-bottom:0.5rem;">${card.difficulty} &bull; ${card.number}</div>
        <div style="font-size:1.2rem; font-weight:700; color:var(--text-primary); line-height:1.5;">${card.question}</div>
      `;
    } else {
      area.innerHTML = `
        <div style="font-size:0.8rem; text-transform:uppercase; color:var(--accent-green); font-weight:700; margin-bottom:0.5rem;">🎓 Senior Answer &bull; ${card.number}</div>
        <div style="font-size:1rem; color:var(--text-primary); line-height:1.6; max-height:260px; overflow-y:auto;">${card.answer}</div>
      `;
    }
  }

  function toggleDeckCardFlip() {
    isDeckCardFlipped = !isDeckCardFlipped;
    renderCurrentDeckCard();
  }

  function stepDeck(delta) {
    if (!activeDeck.length) return;
    currentDeckIndex = clamp(currentDeckIndex + delta, 0, activeDeck.length - 1);
    isDeckCardFlipped = false;
    renderCurrentDeckCard();
  }

  // --- 5. Accordion Fallback Expand/Collapse ---
  function initAccordionQA() {
    document.querySelectorAll('.qa-item').forEach(item => {
      const question = item.querySelector('.qa-question');
      const answer = item.querySelector('.qa-answer');
      const icon = item.querySelector('.expand-icon');
      if (!question || !answer) return;

      answer.style.overflow = 'hidden';
      answer.style.transition = 'max-height 0.3s ease, opacity 0.25s ease';
      answer.style.maxHeight = '0px';
      answer.style.opacity = '0';

      question.addEventListener('click', () => {
        const isExp = item.classList.contains('expanded');
        item.classList.toggle('expanded', !isExp);
        if (icon) icon.style.transform = !isExp ? 'rotate(180deg)' : 'rotate(0deg)';

        if (!isExp) {
          answer.style.maxHeight = `${answer.scrollHeight + 40}px`;
          answer.style.opacity = '1';
        } else {
          answer.style.maxHeight = '0px';
          answer.style.opacity = '0';
        }
      });
    });
  }

  // --- 6. One-Click Code Copy Buttons ---
  function initCodeCopy() {
    document.querySelectorAll('.code-block').forEach(block => {
      if (block.querySelector('.copy-code-btn')) return;

      const header = document.createElement('div');
      header.className = 'code-header';
      header.innerHTML = `
        <span class="code-lang">Kotlin</span>
        <button type="button" class="copy-code-btn" aria-label="Copy code">📋 Copy</button>
      `;

      block.insertBefore(header, block.firstChild);

      const btn = header.querySelector('.copy-code-btn');
      btn.addEventListener('click', e => {
        e.stopPropagation();
        const code = block.querySelector('code') ? block.querySelector('code').textContent.trim() : '';

        const onSuccess = () => {
          btn.innerHTML = '<span>✅ Copied!</span>';
          setTimeout(() => { btn.innerHTML = '<span>📋 Copy</span>'; }, 2000);
        };

        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(code).then(onSuccess).catch(() => fallbackCopy(code, onSuccess));
        } else {
          fallbackCopy(code, onSuccess);
        }
      });
    });
  }

  function fallbackCopy(text, cb) {
    const el = document.createElement('textarea');
    el.value = text;
    el.style.position = 'fixed';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    try { document.execCommand('copy'); cb(); } catch (err) {}
    document.body.removeChild(el);
  }

  // --- 7. Real-Time Global Search ---
  function initSearch() {
    const input = document.getElementById('search-input');
    const resultsContainer = document.getElementById('search-results');
    if (!input || !resultsContainer) return;

    let timer;
    input.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const q = input.value.trim().toLowerCase();
        if (q.length < 2) {
          resultsContainer.innerHTML = '';
          resultsContainer.style.display = 'none';
          return;
        }

        const matches = [];

        // Search subtopics and Q&A in DOM
        document.querySelectorAll('.topic-section').forEach(sec => {
          const topicId = sec.id;
          const topicHeader = sec.querySelector('.topic-header h1');
          const topicTitle = topicHeader ? topicHeader.textContent.trim() : topicId;

          // Subtopics
          sec.querySelectorAll('.subtopic').forEach(sub => {
            const h2 = sub.querySelector('h2');
            const subTitle = h2 ? h2.textContent.trim() : '';
            const text = sub.textContent.toLowerCase();

            if (text.includes(q)) {
              matches.push({
                topicId: topicId,
                topicTitle: topicTitle,
                title: subTitle,
                snippet: sub.querySelector('.card-what p') ? sub.querySelector('.card-what p').textContent.substring(0, 130) + '...' : ''
              });
            }
          });

          // Questions
          sec.querySelectorAll('.qa-item').forEach(qa => {
            const qP = qa.querySelector('.qa-question p');
            const qTxt = qP ? qP.textContent.trim() : '';
            if (qa.textContent.toLowerCase().includes(q)) {
              matches.push({
                topicId: topicId,
                topicTitle: topicTitle,
                title: `🎯 ${qTxt}`,
                snippet: qa.querySelector('.qa-answer p') ? qa.querySelector('.qa-answer p').textContent.substring(0, 130) + '...' : ''
              });
            }
          });
        });

        if (!matches.length) {
          resultsContainer.innerHTML = '<div class="search-result-item" style="color:var(--text-muted);">No matching topics or questions found</div>';
        } else {
          resultsContainer.innerHTML = matches.slice(0, 8).map(m => `
            <div class="search-result-item" data-topic="${m.topicId}">
              <div class="search-result-title">${escapeHtml(m.title)}</div>
              <div class="search-result-topic" style="font-size:0.75rem; color:var(--accent-blue);">${escapeHtml(m.topicTitle)}</div>
              <div class="search-result-snippet" style="font-size:0.8rem; color:var(--text-secondary); margin-top:3px;">${escapeHtml(m.snippet)}</div>
            </div>
          `).join('');

          resultsContainer.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
              const tid = item.getAttribute('data-topic').replace('topic-', '');
              navigateToTopic(tid, true, true);
              resultsContainer.style.display = 'none';
              input.value = '';
            });
          });
        }

        resultsContainer.style.display = 'block';
      }, 200);
    });

    document.addEventListener('click', e => {
      if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
        resultsContainer.style.display = 'none';
      }
    });
  }

  // --- 8. Mobile Sidebar & Scroll Progress ---
  function toggleMobileSidebar(force) {
    const isOpen = typeof force === 'boolean' ? force : !document.body.classList.contains('sidebar-open');
    document.body.classList.toggle('sidebar-open', isOpen);
  }

  function initSidebar() {
    const hb = document.querySelector('.hamburger');
    const overlay = document.querySelector('.sidebar-overlay');
    if (hb) hb.addEventListener('click', () => toggleMobileSidebar());
    if (overlay) overlay.addEventListener('click', () => toggleMobileSidebar(false));
  }

  function updateScrollProgress() {
    const bar = document.getElementById('scroll-progress');
    if (!bar) return;
    const sec = document.getElementById(`topic-${currentTopicId}`);
    if (!sec) { bar.style.width = '0%'; return; }

    const rect = sec.getBoundingClientRect();
    const total = rect.height - window.innerHeight;
    if (total <= 0) { bar.style.width = '100%'; return; }
    const pct = clamp(Math.round((-rect.top / total) * 100), 0, 100);
    bar.style.width = `${pct}%`;
  }

  // --- 9. Dark / Light Theme Toggle ---
  function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEYS.THEME) || 'dark';
    document.documentElement.setAttribute('data-theme', saved);

    document.querySelectorAll('.theme-toggle').forEach(btn => {
      btn.innerHTML = saved === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
      btn.addEventListener('click', () => {
        const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        btn.innerHTML = next === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
        try { localStorage.setItem(STORAGE_KEYS.THEME, next); } catch (e) {}
      });
    });
  }

  // --- 10. Global Keyboard Shortcuts ---
  function initKeyboard() {
    document.addEventListener('keydown', e => {
      const isInput = document.activeElement && ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName);
      const modal = document.querySelector('.flashcard-modal');
      const isModalOpen = modal && modal.classList.contains('active');

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const input = document.getElementById('search-input');
        if (input) { input.focus(); input.select(); }
      } else if (e.key === 'Escape') {
        const res = document.getElementById('search-results');
        if (res) res.style.display = 'none';
        toggleMobileSidebar(false);
        if (isModalOpen) modal.classList.remove('active');
      } else if (isModalOpen) {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          toggleDeckCardFlip();
        } else if (e.key === 'ArrowLeft') {
          e.preventDefault();
          stepDeck(-1);
        } else if (e.key === 'ArrowRight') {
          e.preventDefault();
          stepDeck(1);
        }
      } else if (!isInput) {
        if (e.key === 'ArrowLeft') {
          const prev = Math.max(0, parseInt(currentTopicId, 10) - 1);
          navigateToTopic(prev, true, true);
        } else if (e.key === 'ArrowRight') {
          const next = Math.min(41, parseInt(currentTopicId, 10) + 1);
          navigateToTopic(next, true, true);
        }
      }
    });
  }

  // --- Master App Bootstrapper ---
  function bootApp() {
    initTheme();
    initNavigation();
    enhanceAllQASections();
    initAccordionQA();
    initProgressTracking();
    initCodeCopy();
    initSearch();
    initSidebar();
    initKeyboard();
    window.addEventListener('scroll', updateScrollProgress, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootApp);
  } else {
    bootApp();
  }
})();
