/**
 * Ogden 850 Modern Commute English - Interactive Web Handbook & Audio App
 * 2026 Edition | GitHub Pages Ready
 */

(function () {
  'use strict';

  // State
  const state = {
    episodes: window.OGDEN_MANIFEST || [],
    words: window.OGDEN_WORDS || [],
    currentEpIdx: 0,
    activeFilter: 'all',
    searchQuery: '',
    favorites: new Set(JSON.parse(localStorage.getItem('ogden_favorites') || '[]')),
    theme: localStorage.getItem('ogden_theme') || 'dark',
    playbackRate: 1.0,
    studioWordIdx: 0,
    shadowingTimerInterval: null
  };

  // DOM Elements
  const el = {
    body: document.body,
    html: document.documentElement,
    themeToggle: document.getElementById('btn-theme-toggle'),
    themeIcon: document.getElementById('theme-icon'),
    themeText: document.getElementById('theme-text'),
    btnPresentation: document.getElementById('btn-presentation'),
    
    // Sidebar & Banner
    episodeList: document.getElementById('episode-list'),
    heroBanner: document.getElementById('hero-banner'),
    heroModule: document.getElementById('hero-module-name'),
    heroTitle: document.getElementById('hero-ep-title'),
    heroDesc: document.getElementById('hero-ep-desc'),
    btnPlayEp: document.getElementById('btn-play-episode'),
    heroPlayIcon: document.getElementById('hero-play-icon'),
    heroPlayText: document.getElementById('hero-play-text'),

    // Filter & Search
    filterTabs: document.getElementById('filter-tabs'),
    searchInput: document.getElementById('search-input'),
    searchClear: document.getElementById('search-clear'),
    favCountBadge: document.getElementById('fav-count'),
    cardsContainer: document.getElementById('cards-container'),

    // Audio Player
    audio: document.getElementById('audio-player'),
    equalizer: document.getElementById('equalizer'),
    trackTitle: document.getElementById('player-track-title'),
    trackSub: document.getElementById('player-track-sub'),
    btnPlayPause: document.getElementById('btn-play-pause'),
    btnPrevEp: document.getElementById('btn-prev-ep'),
    btnNextEp: document.getElementById('btn-next-ep'),
    btnRewind: document.getElementById('btn-rewind'),
    btnForward: document.getElementById('btn-forward'),
    timeCurrent: document.getElementById('time-current'),
    timeDuration: document.getElementById('time-duration'),
    progressBarWrap: document.getElementById('progress-bar-wrap'),
    progressFill: document.getElementById('progress-fill'),
    btnSpeed: document.getElementById('btn-speed'),
    volumeSlider: document.getElementById('volume-slider'),

    // Presentation Modal
    modal: document.getElementById('presentation-modal'),
    btnCloseStudio: document.getElementById('btn-close-studio'),
    studioEpName: document.getElementById('studio-ep-name'),
    studioWord: document.getElementById('studio-word'),
    studioZh: document.getElementById('studio-zh'),
    studioCore: document.getElementById('studio-core'),
    studioExEn: document.getElementById('studio-ex-en'),
    studioExZh: document.getElementById('studio-ex-zh'),
    shadowingTimer: document.getElementById('shadowing-timer'),
    shadowingFill: document.getElementById('shadowing-fill'),
    studioBtnPrev: document.getElementById('studio-btn-prev'),
    studioBtnNext: document.getElementById('studio-btn-next'),
    studioBtnSpeak: document.getElementById('studio-btn-speak'),
    studioCounter: document.getElementById('studio-counter')
  };

  // Category Names Map
  const categoryNames = {
    all: '全部 (850)',
    op: 'Operations 操作詞',
    gt: 'General Things 通用名詞',
    pt: 'Picturable Things 具象名詞',
    qg: 'Qualities 性質形容詞',
    qo: 'Opposites 成對反義詞'
  };

  // Module Descriptions
  const moduleDescriptions = {
    op: '英語對話的動力心臟。18 個核心動詞搭配方向介系詞即可替換 80% 的生僻動詞！',
    gt: '建構事物本質與抽象概念。涵蓋時間、空間、關係與社會運作的核心名詞。',
    pt: '眼睛看得見、手摸得到的實體名詞。居家、科技、自然與人體器官的必備詞彙。',
    qg: '描述事物狀態、特質與程度的基礎形容詞，賦予表達精準的情境氛圍。',
    qo: '成對出現的高頻反義形容詞，透過兩極對比強化大腦聯想記憶！'
  };

  /* ------------------------------------------------------------------------
     1. Initialization
     ------------------------------------------------------------------------ */
  function init() {
    applyTheme(state.theme);
    updateFavCount();
    renderSidebarEpisodes();
    updateHeroBanner(state.currentEpIdx);
    loadEpisodeAudio(state.currentEpIdx, false);
    renderCards();
    setupEventListeners();
  }

  /* ------------------------------------------------------------------------
     2. Theme Management
     ------------------------------------------------------------------------ */
  function applyTheme(theme) {
    state.theme = theme;
    el.html.setAttribute('data-theme', theme);
    localStorage.setItem('ogden_theme', theme);
    if (theme === 'dark') {
      el.themeIcon.textContent = '🌙';
      el.themeText.textContent = '深色模式';
    } else {
      el.themeIcon.textContent = '☀️';
      el.themeText.textContent = '淺色模式';
    }
  }

  function toggleTheme() {
    const nextTheme = state.theme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
  }

  /* ------------------------------------------------------------------------
     3. Sidebar & Hero Episode Management
     ------------------------------------------------------------------------ */
  function renderSidebarEpisodes() {
    el.episodeList.innerHTML = '';
    const fragment = document.createDocumentFragment();

    state.episodes.forEach((ep, idx) => {
      const item = document.createElement('button');
      item.className = `episode-item ${idx === state.currentEpIdx ? 'active' : ''}`;
      item.setAttribute('data-idx', idx);

      const count = ep.end - ep.start;
      item.innerHTML = `
        <span class="ep-badge font-mono">Ep ${String(ep.ep).padStart(2, '0')}</span>
        <div class="ep-meta">
          <div class="ep-name">${escapeHTML(ep.title)}</div>
          <div class="ep-count">${count} 詞 | #${ep.start + 1}~#${ep.end}</div>
        </div>
        <span class="ep-play-btn">${idx === state.currentEpIdx && !el.audio.paused ? '⏸' : '▶'}</span>
      `;

      item.addEventListener('click', () => {
        selectEpisode(idx, true);
      });

      fragment.appendChild(item);
    });

    el.episodeList.appendChild(fragment);
  }

  function selectEpisode(idx, autoPlay = true) {
    if (idx < 0 || idx >= state.episodes.length) return;
    state.currentEpIdx = idx;

    // Update active highlight in sidebar
    document.querySelectorAll('.episode-item').forEach((btn, i) => {
      btn.classList.toggle('active', i === idx);
      const playIcon = btn.querySelector('.ep-play-btn');
      if (playIcon) {
        playIcon.textContent = i === idx && !el.audio.paused ? '⏸' : '▶';
      }
    });

    updateHeroBanner(idx);
    loadEpisodeAudio(idx, autoPlay);

    // Scroll to first card of this episode
    const currentEp = state.episodes[idx];
    const targetWordId = currentEp.start + 1;
    const targetCard = document.getElementById(`word-card-${targetWordId}`);
    if (targetCard) {
      targetCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function updateHeroBanner(idx) {
    const ep = state.episodes[idx];
    if (!ep) return;

    el.heroModule.textContent = ep.catName;
    el.heroTitle.textContent = `Episode ${String(ep.ep).padStart(2, '0')}：${ep.title}`;
    el.heroDesc.textContent = moduleDescriptions[ep.cat] || '奧格登基本英語 850 廣播級現代通勤雙語沉浸式音訊課程。';
    updateHeroPlayButton();
  }

  function updateHeroPlayButton() {
    if (el.audio.paused) {
      el.heroPlayIcon.textContent = '▶';
      el.heroPlayText.textContent = '收聽本集音訊';
    } else {
      el.heroPlayIcon.textContent = '⏸';
      el.heroPlayText.textContent = '暫停音訊播放';
    }
  }

  /* ------------------------------------------------------------------------
     4. Audio Player Logic
     ------------------------------------------------------------------------ */
  function loadEpisodeAudio(idx, autoPlay = false) {
    const ep = state.episodes[idx];
    if (!ep) return;

    el.audio.src = `audio/${ep.file}`;
    el.audio.playbackRate = state.playbackRate;
    el.trackTitle.textContent = `Episode ${String(ep.ep).padStart(2, '0')}：${ep.title}`;
    el.trackSub.textContent = `${ep.catName} | #${ep.start + 1} ~ #${ep.end} 詞`;

    if (autoPlay) {
      el.audio.play().catch(e => console.log('Autoplay policy caught:', e));
    }
  }

  function togglePlayPause() {
    if (el.audio.paused) {
      el.audio.play();
    } else {
      el.audio.pause();
    }
  }

  function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  function updateProgress() {
    const current = el.audio.currentTime || 0;
    const duration = el.audio.duration || 0;
    el.timeCurrent.textContent = formatTime(current);
    el.timeDuration.textContent = formatTime(duration);

    if (duration > 0) {
      const pct = (current / duration) * 100;
      el.progressFill.style.width = `${pct}%`;
    }
  }

  function scrubProgress(e) {
    const rect = el.progressBarWrap.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    const clamped = Math.max(0, Math.min(1, pos));
    if (el.audio.duration) {
      el.audio.currentTime = clamped * el.audio.duration;
    }
  }

  function cyclePlaybackSpeed() {
    const speeds = [0.8, 1.0, 1.2, 1.5];
    const currIdx = speeds.indexOf(state.playbackRate);
    const nextIdx = (currIdx + 1) % speeds.length;
    state.playbackRate = speeds[nextIdx];
    el.audio.playbackRate = state.playbackRate;
    el.btnSpeed.textContent = `${state.playbackRate.toFixed(1)}x`;
  }

  /* ------------------------------------------------------------------------
     5. Word Cards Rendering & Filtering
     ------------------------------------------------------------------------ */
  function renderCards() {
    const query = state.searchQuery.toLowerCase().trim();
    const filter = state.activeFilter;

    const filtered = state.words.filter(word => {
      // Category / Favorite filter
      if (filter === 'fav') {
        if (!state.favorites.has(word.id)) return false;
      } else if (filter !== 'all') {
        if (word.c !== filter) return false;
      }

      // Search query filter
      if (query) {
        const matchWord = word.w.toLowerCase().includes(query);
        const matchZh = word.zh && word.zh.toLowerCase().includes(query);
        const matchCore = word.core && word.core.toLowerCase().includes(query);
        const matchEx = word.ex && word.ex.toLowerCase().includes(query);
        const matchExz = word.exz && word.exz.toLowerCase().includes(query);
        const matchSyn = word.s && word.s.some(s => s.toLowerCase().includes(query));
        return matchWord || matchZh || matchCore || matchEx || matchExz || matchSyn;
      }

      return true;
    });

    el.cardsContainer.innerHTML = '';
    if (filtered.length === 0) {
      el.cardsContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
          <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
          <h3 style="font-size: 1.2rem; color: var(--text-primary); margin-bottom: 0.5rem;">查無相符的單字或內容</h3>
          <p>請嘗試其他中英文關鍵字，或切換上方分類標籤。</p>
        </div>
      `;
      return;
    }

    const fragment = document.createDocumentFragment();

    filtered.forEach(word => {
      const isFav = state.favorites.has(word.id);
      const card = document.createElement('article');
      card.className = 'word-card';
      card.id = `word-card-${word.id}`;

      // Build Synonyms
      const synHtml = (word.s && word.s.length > 0)
        ? word.s.map(s => `<span class="syn-tag" data-syn="${escapeHTML(s)}">${escapeHTML(s)}</span>`).join('')
        : '';

      card.innerHTML = `
        <div class="card-top">
          <span class="word-id-pill">#${String(word.id).padStart(3, '0')}</span>
          <div class="card-badges">
            <span class="cat-pill cat-${word.c}">${word.c.toUpperCase()}</span>
            <button class="bookmark-btn ${isFav ? 'bookmarked' : ''}" data-id="${word.id}" title="${isFav ? '取消收藏' : '加入收藏'}">
              ${isFav ? '★' : '☆'}
            </button>
          </div>
        </div>

        <div class="card-header-main">
          <div class="word-title-group">
            <span class="word-text">${escapeHTML(word.w)}</span>
            <span class="word-zh">${escapeHTML(word.zh)}</span>
          </div>
          <button class="btn-speak" data-speak-word="${escapeHTML(word.w)}" title="慢速朗讀單字">
            🔊
          </button>
        </div>

        <div class="core-box">
          <div class="core-label">
            <span>💡</span>
            <span>核心意象 (Core Sense)</span>
          </div>
          <p class="core-text">${escapeHTML(word.core || '')}</p>
        </div>

        <div class="example-box">
          <div class="ex-top">
            <p class="ex-en">${escapeHTML(word.ex || '')}</p>
            <button class="btn-speak" data-speak-sentence="${escapeHTML(word.ex || '')}" title="朗讀例句" style="width:26px; height:26px; font-size:0.75rem;">
              🔊
            </button>
          </div>
          <p class="ex-zh">${escapeHTML(word.exz || '')}</p>
        </div>

        ${synHtml ? `
        <div class="synonyms-row">
          <span style="color:var(--text-muted); font-size:0.72rem;">代換近義：</span>
          ${synHtml}
        </div>` : ''}
      `;

      fragment.appendChild(card);
    });

    el.cardsContainer.appendChild(fragment);
  }

  function updateFavCount() {
    el.favCountBadge.textContent = state.favorites.size;
  }

  function toggleFavorite(id) {
    if (state.favorites.has(id)) {
      state.favorites.delete(id);
    } else {
      state.favorites.add(id);
    }
    localStorage.setItem('ogden_favorites', JSON.stringify(Array.from(state.favorites)));
    updateFavCount();

    // Update active button icon
    const btns = document.querySelectorAll(`.bookmark-btn[data-id="${id}"]`);
    btns.forEach(b => {
      const isFav = state.favorites.has(id);
      b.classList.toggle('bookmarked', isFav);
      b.textContent = isFav ? '★' : '☆';
      b.title = isFav ? '取消收藏' : '加入收藏';
    });

    // If currently filtering favorites, re-render
    if (state.activeFilter === 'fav') {
      renderCards();
    }
  }

  /* ------------------------------------------------------------------------
     6. Web Speech Synthesis (In-Browser Fallback & Quick Audio)
     ------------------------------------------------------------------------ */
  function speakEnglish(text, rate = 0.8) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = rate;

    // Pick native US English voice if available
    const voices = window.speechSynthesis.getVoices();
    const usVoice = voices.find(v => v.lang === 'en-US' && (v.name.includes('Natural') || v.name.includes('Jenny') || v.name.includes('Samantha')));
    if (usVoice) {
      utterance.voice = usVoice;
    }

    window.speechSynthesis.speak(utterance);
  }

  /* ------------------------------------------------------------------------
     7. YouTube 16:9 Presentation Studio Mode
     ------------------------------------------------------------------------ */
  function openPresentationStudio(wordIndex = 0) {
    state.studioWordIdx = wordIndex;
    updateStudioContent();
    el.modal.classList.add('active');
  }

  function closePresentationStudio() {
    el.modal.classList.remove('active');
    stopShadowingCountdown();
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  }

  function updateStudioContent() {
    const word = state.words[state.studioWordIdx];
    if (!word) return;

    el.studioEpName.textContent = `Episode ${String(word.ep).padStart(2, '0')}：${word.epTitle}`;
    el.studioWord.textContent = word.w.toUpperCase();
    el.studioZh.textContent = word.zh;
    el.studioCore.textContent = `💡 ${word.core}`;
    el.studioExEn.textContent = `"${word.ex}"`;
    el.studioExZh.textContent = word.exz;
    el.studioCounter.textContent = `Word ${String(word.id).padStart(3, '0')} / 850`;

    // Start Shadowing 3.5s Countdown visualizer
    startShadowingCountdown();
  }

  function startShadowingCountdown() {
    stopShadowingCountdown();
    let timeLeft = 3.5;
    const total = 3.5;
    el.shadowingTimer.textContent = `${timeLeft.toFixed(1)}s`;
    el.shadowingFill.style.width = '100%';

    const interval = 50; // 50ms ticks
    state.shadowingTimerInterval = setInterval(() => {
      timeLeft -= interval / 1000;
      if (timeLeft <= 0) {
        timeLeft = 0;
        stopShadowingCountdown();
      }
      el.shadowingTimer.textContent = `${timeLeft.toFixed(1)}s`;
      const pct = (timeLeft / total) * 100;
      el.shadowingFill.style.width = `${pct}%`;
    }, interval);
  }

  function stopShadowingCountdown() {
    if (state.shadowingTimerInterval) {
      clearInterval(state.shadowingTimerInterval);
      state.shadowingTimerInterval = null;
    }
  }

  function studioNextWord() {
    if (state.studioWordIdx < state.words.length - 1) {
      state.studioWordIdx++;
      updateStudioContent();
    }
  }

  function studioPrevWord() {
    if (state.studioWordIdx > 0) {
      state.studioWordIdx--;
      updateStudioContent();
    }
  }

  /* ------------------------------------------------------------------------
     8. Event Listeners Setup
     ------------------------------------------------------------------------ */
  function setupEventListeners() {
    // Theme toggle
    el.themeToggle.addEventListener('click', toggleTheme);

    // Audio Play/Pause
    el.btnPlayPause.addEventListener('click', togglePlayPause);
    el.btnPlayEp.addEventListener('click', () => {
      togglePlayPause();
    });

    el.audio.addEventListener('play', () => {
      el.btnPlayPause.textContent = '⏸';
      el.equalizer.classList.add('is-playing');
      updateHeroPlayButton();
      renderSidebarEpisodes();
    });

    el.audio.addEventListener('pause', () => {
      el.btnPlayPause.textContent = '▶';
      el.equalizer.classList.remove('is-playing');
      updateHeroPlayButton();
      renderSidebarEpisodes();
    });

    el.audio.addEventListener('timeupdate', updateProgress);

    el.audio.addEventListener('ended', () => {
      // Automatically advance to next episode
      if (state.currentEpIdx < state.episodes.length - 1) {
        selectEpisode(state.currentEpIdx + 1, true);
      }
    });

    // Audio Navigation
    el.btnPrevEp.addEventListener('click', () => {
      if (state.currentEpIdx > 0) selectEpisode(state.currentEpIdx - 1, true);
    });

    el.btnNextEp.addEventListener('click', () => {
      if (state.currentEpIdx < state.episodes.length - 1) selectEpisode(state.currentEpIdx + 1, true);
    });

    el.btnRewind.addEventListener('click', () => {
      el.audio.currentTime = Math.max(0, el.audio.currentTime - 10);
    });

    el.btnForward.addEventListener('click', () => {
      el.audio.currentTime = Math.min(el.audio.duration || 0, el.audio.currentTime + 10);
    });

    el.progressBarWrap.addEventListener('click', scrubProgress);
    el.btnSpeed.addEventListener('click', cyclePlaybackSpeed);

    el.volumeSlider.addEventListener('input', (e) => {
      el.audio.volume = parseFloat(e.target.value);
    });

    // Category Tabs Filter
    el.filterTabs.addEventListener('click', (e) => {
      const tab = e.target.closest('.filter-tab');
      if (!tab) return;
      document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.activeFilter = tab.getAttribute('data-cat');
      renderCards();
    });

    // Real-time Search
    el.searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      el.searchClear.classList.toggle('show', !!state.searchQuery);
      renderCards();
    });

    el.searchClear.addEventListener('click', () => {
      el.searchInput.value = '';
      state.searchQuery = '';
      el.searchClear.classList.remove('show');
      renderCards();
    });

    // Delegation on Cards Container (Bookmark, Speak, Synonyms)
    el.cardsContainer.addEventListener('click', (e) => {
      // Bookmark
      const favBtn = e.target.closest('.bookmark-btn');
      if (favBtn) {
        const id = parseInt(favBtn.getAttribute('data-id'), 10);
        toggleFavorite(id);
        return;
      }

      // Speak word
      const speakWordBtn = e.target.closest('[data-speak-word]');
      if (speakWordBtn) {
        const wordText = speakWordBtn.getAttribute('data-speak-word');
        speakEnglish(wordText, 0.75);
        return;
      }

      // Speak sentence
      const speakExBtn = e.target.closest('[data-speak-sentence]');
      if (speakExBtn) {
        const sentenceText = speakExBtn.getAttribute('data-speak-sentence');
        speakEnglish(sentenceText, 0.85);
        return;
      }

      // Click synonym to search
      const synTag = e.target.closest('.syn-tag');
      if (synTag) {
        const syn = synTag.getAttribute('data-syn');
        el.searchInput.value = syn;
        state.searchQuery = syn;
        el.searchClear.classList.add('show');
        renderCards();
      }
    });

    // Presentation Modal Controls
    el.btnPresentation.addEventListener('click', () => {
      openPresentationStudio(state.episodes[state.currentEpIdx].start);
    });

    el.btnCloseStudio.addEventListener('click', closePresentationStudio);
    el.studioBtnNext.addEventListener('click', studioNextWord);
    el.studioBtnPrev.addEventListener('click', studioPrevWord);

    el.studioBtnSpeak.addEventListener('click', () => {
      const word = state.words[state.studioWordIdx];
      if (word) {
        speakEnglish(word.w, 0.75);
        startShadowingCountdown();
      }
    });

    // Global Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      // Escape closes modal
      if (e.key === 'Escape') {
        if (el.modal.classList.contains('active')) {
          closePresentationStudio();
        } else if (state.searchQuery) {
          el.searchInput.value = '';
          state.searchQuery = '';
          el.searchClear.classList.remove('show');
          renderCards();
        }
      }

      // In Studio Modal: Left/Right arrows navigate
      if (el.modal.classList.contains('active')) {
        if (e.key === 'ArrowRight' || e.key === 'PageDown') {
          studioNextWord();
        } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
          studioPrevWord();
        } else if (e.key === ' ') {
          e.preventDefault();
          const word = state.words[state.studioWordIdx];
          if (word) speakEnglish(word.w, 0.75);
        }
        return;
      }

      // Shortcut '/' to focus search
      if (e.key === '/' && document.activeElement !== el.searchInput) {
        e.preventDefault();
        el.searchInput.focus();
      }

      // Space to toggle audio (if not typing in input)
      if (e.key === ' ' && document.activeElement !== el.searchInput) {
        e.preventDefault();
        togglePlayPause();
      }
    });
  }

  // HTML Sanitizer
  function escapeHTML(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
